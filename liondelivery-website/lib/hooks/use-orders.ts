"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ordersApi, type CreateOrderPayload, type Order } from "@/lib/api/orders";

export const orderKeys = {
  all: ["orders"] as const,
  byNumber: (number: string) => [...orderKeys.all, "number", number] as const,
};

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
 * Hook to create a new order
 */
export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateOrderPayload) => ordersApi.create(payload),
    onSuccess: () => {
      // Invalidate and refetch orders
      queryClient.invalidateQueries({ queryKey: orderKeys.all });
    },
  });
}
