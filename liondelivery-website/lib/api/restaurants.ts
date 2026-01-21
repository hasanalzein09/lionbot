import { get } from "./client";
import type { Restaurant, RestaurantListResponse, RestaurantFilters } from "@/types/restaurant";

// Using /public endpoints - no authentication required
const PUBLIC_PREFIX = "/public";

export const restaurantsApi = {
  /**
   * Get all restaurants with optional filters
   */
  getAll: async (filters?: RestaurantFilters): Promise<RestaurantListResponse> => {
    const response = await get<{ restaurants: Restaurant[]; total: number; has_more: boolean }>(
      `${PUBLIC_PREFIX}/restaurants/`,
      {
        category_id: filters?.category,
        search: filters?.search,
        sort: filters?.sortBy,
        offset: filters?.page ? (filters.page - 1) * (filters.limit || 12) : 0,
        limit: filters?.limit || 12,
      }
    );

    return {
      restaurants: response.restaurants || [],
      total: response.total || 0,
      page: filters?.page || 1,
      limit: filters?.limit || 12,
      hasMore: response.has_more || false,
    };
  },

  /**
   * Get featured restaurants
   */
  getFeatured: async (limit = 6): Promise<Restaurant[]> => {
    return get<Restaurant[]>(`${PUBLIC_PREFIX}/featured/restaurants/`, { limit });
  },

  /**
   * Get a single restaurant by slug
   */
  getBySlug: async (slug: string): Promise<Restaurant> => {
    return get<Restaurant>(`${PUBLIC_PREFIX}/restaurants/slug/${slug}`);
  },

  /**
   * Get restaurant by ID
   */
  getById: async (id: string): Promise<Restaurant> => {
    return get<Restaurant>(`${PUBLIC_PREFIX}/restaurants/${id}`);
  },

  /**
   * Search restaurants
   */
  search: async (query: string, limit = 10): Promise<Restaurant[]> => {
    const response = await get<{ restaurants: Restaurant[] }>(`${PUBLIC_PREFIX}/search/`, {
      q: query,
      limit,
    });
    return response.restaurants || [];
  },

  /**
   * Get restaurants by category
   */
  getByCategory: async (categoryId: string, limit = 12): Promise<Restaurant[]> => {
    const response = await get<{ restaurants: Restaurant[] }>(`${PUBLIC_PREFIX}/restaurants/`, {
      category_id: categoryId,
      limit,
    });
    return response.restaurants || [];
  },
};
