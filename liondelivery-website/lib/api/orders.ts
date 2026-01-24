import { get, post } from "./client";

// Using /public endpoints - no authentication required
const PUBLIC_PREFIX = "/public";

export type OrderStatus =
  | "new"
  | "accepted"
  | "preparing"
  | "ready"
  | "out_for_delivery"
  | "delivered"
  | "cancelled";

export interface OrderItem {
  id: number;
  name: string;
  name_ar?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Order {
  id: number;
  order_number: string;
  status: OrderStatus;
  total: number;
  delivery_fee: number;
  subtotal?: number;
  address?: string;
  is_scheduled?: boolean;
  scheduled_time?: string | null;
  restaurant: {
    id: number;
    name: string;
    name_ar?: string;
    phone?: string;
  } | null;
  customer: {
    name: string;
    phone: string;
  } | null;
  items: OrderItem[];
  created_at: string;
}

export interface CreateOrderPayload {
  restaurant_id: number;
  items: {
    product_id: number;
    name: string;
    name_ar: string | null;
    price: number;
    quantity: number;
    variant_id: number | null;
    variant_name: string | null;
    variant_price: number | null;
    notes: string | null;
  }[];
  customer: {
    name: string;
    phone: string;
    address: string;
  };
  notes: string | null;
  payment_method: "cash" | "card";
  scheduled_time: string | null;
}

export interface CreateOrderResponse {
  success: boolean;
  order: {
    id: number;
    order_number: string;
    status: string;
    total: number;
    delivery_fee: number;
    subtotal: number;
    is_scheduled?: boolean;
    scheduled_time?: string | null;
    restaurant: {
      id: number;
      name: string;
      name_ar?: string;
    };
    customer: {
      name: string;
      phone: string;
      address: string;
    };
    created_at: string;
  };
  message?: string;
}

export const ordersApi = {
  /**
   * Create a new order (public endpoint - no auth required)
   */
  create: async (payload: CreateOrderPayload): Promise<CreateOrderResponse> => {
    return post<CreateOrderResponse>(`${PUBLIC_PREFIX}/orders/`, payload);
  },

  /**
   * Get order by order number (public endpoint)
   */
  getByNumber: async (orderNumber: string): Promise<Order> => {
    return get<Order>(`${PUBLIC_PREFIX}/orders/${orderNumber}`);
  },
};
