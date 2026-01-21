import { get } from "./client";
import type { Menu, MenuCategory, MenuItem, MenuResponse } from "@/types/menu";

// Using /public endpoints - no authentication required
const PUBLIC_PREFIX = "/public";

export const menusApi = {
  /**
   * Get menu for a restaurant
   */
  getByRestaurant: async (restaurantId: string): Promise<Menu> => {
    const response = await get<{ restaurant_id: number; categories: MenuCategory[] }>(
      `${PUBLIC_PREFIX}/restaurants/${restaurantId}/menu`
    );

    return {
      restaurantId: String(response.restaurant_id),
      categories: response.categories || [],
    };
  },

  /**
   * Get menu categories for a restaurant
   */
  getCategories: async (restaurantId: string): Promise<MenuCategory[]> => {
    const response = await get<{ categories: MenuCategory[] }>(`/restaurants/${restaurantId}/menu/categories`);
    return response.categories || [];
  },

  /**
   * Get menu items for a category
   */
  getItemsByCategory: async (restaurantId: string, categoryId: string): Promise<MenuItem[]> => {
    const response = await get<{ items: MenuItem[] }>(
      `/restaurants/${restaurantId}/menu/categories/${categoryId}/items`
    );
    return response.items || [];
  },

  /**
   * Get a single menu item
   */
  getItem: async (restaurantId: string, itemId: string): Promise<MenuItem> => {
    return get<MenuItem>(`/restaurants/${restaurantId}/menu/items/${itemId}`);
  },

  /**
   * Search menu items
   */
  search: async (restaurantId: string, query: string): Promise<MenuItem[]> => {
    const response = await get<{ items: MenuItem[] }>(`/restaurants/${restaurantId}/menu/search`, {
      q: query,
    });
    return response.items || [];
  },

  /**
   * Get popular items for a restaurant
   */
  getPopularItems: async (restaurantId: string, limit = 5): Promise<MenuItem[]> => {
    const response = await get<{ items: MenuItem[] }>(`/restaurants/${restaurantId}/menu/popular`, {
      limit,
    });
    return response.items || [];
  },
};
