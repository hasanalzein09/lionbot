"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ordersApi, type CreateOrderPayload, type Order } from "@/lib/api/orders";

export const orderKeys = {
  all: ["orders"] as const,
  byId: (id: string) => [...orderKeys.all, id] as const,
  byNumber: (number: string) => [...orderKeys.all, "number", number] as const,
  byPhone: (phone: string) => [...orderKeys.all, "phone", phone] as const,
  track: (id: string) => [...orderKeys.all, "track", id] as const,
};

/**
 * Hook to fetch an order by ID
 */
export function useOrder(orderId: string) {
  return useQuery({
    queryKey: orderKeys.byId(orderId),
    queryFn: () => ordersApi.getById(orderId),
    enabled: !!orderId,
  });
}

/**
 * Hook to fetch an order by order number
 */
export function useOrderByNumber(orderNumber: string) {
  return useQuery({
    queryKey: orderKeys.byNumber(orderNumber),
    queryFn: () => ordersApi.getByNumber(orderNumber),
    enabled: !!orderNumber,
  });
}

/**
 * Hook to fetch orders by phone number
 */
export function useOrdersByPhone(phone: string) {
  return useQuery({
    queryKey: orderKeys.byPhone(phone),
    queryFn: () => ordersApi.getByPhone(phone),
    enabled: !!phone,
  });
}

/**
 * Hook to track an order
 */
export function useTrackOrder(orderId: string) {
  return useQuery({
    queryKey: orderKeys.track(orderId),
    queryFn: () => ordersApi.trackOrder(orderId),
    enabled: !!orderId,
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

/**
 * Hook to create a new order
 */
export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateOrderPayload) => ordersApi.create(payload),
    onSuccess: (data) => {
      // Invalidate and refetch orders
      queryClient.invalidateQueries({ queryKey: orderKeys.all });
    },
  });
}

/**
 * Hook to cancel an order
 */
export function useCancelOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ orderId, reason }: { orderId: string; reason?: string }) =>
      ordersApi.cancel(orderId, reason),
    onSuccess: (data, variables) => {
      // Update the order in cache
      queryClient.setQueryData(orderKeys.byId(variables.orderId), data);
      queryClient.invalidateQueries({ queryKey: orderKeys.all });
    },
  });
}
