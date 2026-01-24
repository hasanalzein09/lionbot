"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { orderKeys } from "./use-orders";
import type { OrderStatus } from "@/lib/api/orders";

interface OrderUpdate {
  type: "order_update";
  order_id: number;
  status: OrderStatus;
  driver_location?: {
    latitude: number;
    longitude: number;
  };
}

interface UseOrderTrackingOptions {
  onStatusChange?: (newStatus: OrderStatus) => void;
  onDriverLocationUpdate?: (location: { latitude: number; longitude: number }) => void;
  enabled?: boolean;
}

// Get WebSocket URL from environment or default
const getWsUrl = () => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://lion.hmz.technology/api/v1";
  // Convert https to wss, remove /api/v1 path
  return apiUrl.replace(/^https?:\/\//, "wss://").replace(/\/api\/v1$/, "");
};

/**
 * Hook for real-time order tracking via WebSocket
 * Automatically updates the order cache when status changes
 */
export function useOrderTracking(
  orderId: number | string | undefined,
  options: UseOrderTrackingOptions = {}
) {
  const { onStatusChange, onDriverLocationUpdate, enabled = true } = options;
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastStatus, setLastStatus] = useState<OrderStatus | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (!orderId || !enabled) return;

    // Don't reconnect if already connected
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const wsUrl = `${getWsUrl()}/ws/order/${orderId}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log(`[OrderTracking] Connected to order ${orderId}`);
        setIsConnected(true);
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data: OrderUpdate = JSON.parse(event.data);

          if (data.type === "order_update") {
            // Update local state
            setLastStatus(data.status);

            // Call the callback if provided
            if (onStatusChange) {
              onStatusChange(data.status);
            }

            // Update the React Query cache
            queryClient.setQueryData(
              orderKeys.byNumber(`LN-${String(data.order_id).padStart(6, "0")}`),
              (oldData: any) => {
                if (!oldData) return oldData;
                return {
                  ...oldData,
                  status: data.status,
                };
              }
            );

            // Handle driver location update
            if (data.driver_location && onDriverLocationUpdate) {
              onDriverLocationUpdate(data.driver_location);
            }
          }
        } catch (e) {
          console.error("[OrderTracking] Failed to parse message:", e);
        }
      };

      ws.onclose = (event) => {
        console.log(`[OrderTracking] Disconnected from order ${orderId}`, event.code);
        setIsConnected(false);

        // Attempt to reconnect if not intentionally closed
        if (enabled && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectAttempts.current++;
          console.log(`[OrderTracking] Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };

      ws.onerror = (error) => {
        console.error("[OrderTracking] WebSocket error:", error);
      };
    } catch (error) {
      console.error("[OrderTracking] Failed to create WebSocket:", error);
    }
  }, [orderId, enabled, onStatusChange, onDriverLocationUpdate, queryClient]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
  }, []);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Reconnect when orderId or enabled changes
  useEffect(() => {
    if (enabled && orderId) {
      reconnectAttempts.current = 0;
      connect();
    } else {
      disconnect();
    }
  }, [orderId, enabled, connect, disconnect]);

  return {
    isConnected,
    lastStatus,
    disconnect,
    reconnect: connect,
  };
}
