import { get, post } from "./client";
import type { CartItem } from "@/lib/stores/cart-store";

export type OrderStatus =
  | "pending"
  | "confirmed"
  | "preparing"
  | "ready"
  | "delivering"
  | "delivered"
  | "cancelled";

export interface OrderItem {
  id: string;
  productId: string;
  name: string;
  nameAr?: string;
  price: number;
  quantity: number;
  variant?: {
    id: string;
    name: string;
    nameAr?: string;
    price: number;
  };
  addons?: {
    id: string;
    name: string;
    nameAr?: string;
    price: number;
    quantity: number;
  }[];
  notes?: string;
  total: number;
}

export interface Order {
  id: string;
  orderNumber: string;
  status: OrderStatus;
  items: OrderItem[];
  restaurant: {
    id: string;
    name: string;
    nameAr?: string;
    image?: string;
    phone?: string;
  };
  customer: {
    name: string;
    phone: string;
    address: string;
  };
  subtotal: number;
  deliveryFee: number;
  discount: number;
  total: number;
  paymentMethod: "cash" | "card";
  notes?: string;
  estimatedDeliveryTime?: number;
  createdAt: string;
  updatedAt: string;
}

export interface CreateOrderPayload {
  restaurantId: string;
  items: Omit<CartItem, "id" | "restaurantId" | "restaurantName" | "restaurantNameAr">[];
  customer: {
    name: string;
    phone: string;
    address: string;
  };
  notes?: string;
  promoCode?: string;
  paymentMethod: "cash" | "card";
}

export interface CreateOrderResponse {
  success: boolean;
  order: Order;
  message?: string;
}

export const ordersApi = {
  /**
   * Create a new order
   */
  create: async (payload: CreateOrderPayload): Promise<CreateOrderResponse> => {
    return post<CreateOrderResponse>("/orders", payload);
  },

  /**
   * Get order by ID
   */
  getById: async (orderId: string): Promise<Order> => {
    return get<Order>(`/orders/${orderId}`);
  },

  /**
   * Get order by order number
   */
  getByNumber: async (orderNumber: string): Promise<Order> => {
    return get<Order>(`/orders/number/${orderNumber}`);
  },

  /**
   * Get orders by phone number (for order history)
   */
  getByPhone: async (phone: string): Promise<Order[]> => {
    const response = await get<{ orders: Order[] }>("/orders", { phone });
    return response.orders || [];
  },

  /**
   * Track order status
   */
  trackOrder: async (orderId: string): Promise<Order> => {
    return get<Order>(`/orders/${orderId}/track`);
  },

  /**
   * Cancel order
   */
  cancel: async (orderId: string, reason?: string): Promise<Order> => {
    return post<Order>(`/orders/${orderId}/cancel`, { reason });
  },
};
