import { get } from "./client";

const PUBLIC_PREFIX = "/public";

export interface TimeSlot {
  time: string;
  display: string;
  display_ar: string;
  datetime: string;
}

export interface DateSlots {
  date: string;
  date_display: string;
  slots: TimeSlot[];
}

export interface DeliverySlotsResponse {
  restaurant_id: number;
  dates: DateSlots[];
}

export const schedulingApi = {
  /**
   * Get available delivery time slots for a restaurant
   */
  getSlots: async (restaurantId: number, date?: string): Promise<DeliverySlotsResponse> => {
    const params: Record<string, string | number | undefined> = {};
    if (date) {
      params.date = date;
    }
    return get<DeliverySlotsResponse>(
      `${PUBLIC_PREFIX}/restaurants/${restaurantId}/delivery-slots`,
      params
    );
  },
};
