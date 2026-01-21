import { get } from "./client";
import type { Restaurant } from "@/types/restaurant";
import type { MenuItem } from "@/types/menu";

export interface SearchResults {
  restaurants: Restaurant[];
  items: MenuItem[];
  total: number;
}

export interface SearchSuggestion {
  type: "restaurant" | "item" | "category";
  id: string;
  name: string;
  nameAr?: string;
  image?: string;
  restaurantId?: string;
  restaurantName?: string;
}

export const searchApi = {
  /**
   * Global search across restaurants and menu items
   */
  search: async (query: string, limit = 20): Promise<SearchResults> => {
    const response = await get<SearchResults>("/search", {
      q: query,
      limit,
    });
    return {
      restaurants: response.restaurants || [],
      items: response.items || [],
      total: response.total || 0,
    };
  },

  /**
   * Get search suggestions (autocomplete)
   */
  getSuggestions: async (query: string, limit = 8): Promise<SearchSuggestion[]> => {
    const response = await get<{ suggestions: SearchSuggestion[] }>("/search/suggestions", {
      q: query,
      limit,
    });
    return response.suggestions || [];
  },

  /**
   * Search restaurants only
   */
  searchRestaurants: async (query: string, limit = 10): Promise<Restaurant[]> => {
    const response = await get<{ restaurants: Restaurant[] }>("/search/restaurants", {
      q: query,
      limit,
    });
    return response.restaurants || [];
  },

  /**
   * Search menu items only
   */
  searchItems: async (query: string, limit = 10): Promise<MenuItem[]> => {
    const response = await get<{ items: MenuItem[] }>("/search/items", {
      q: query,
      limit,
    });
    return response.items || [];
  },

  /**
   * Get popular searches
   */
  getPopular: async (limit = 5): Promise<string[]> => {
    const response = await get<{ searches: string[] }>("/search/popular", {
      limit,
    });
    return response.searches || [];
  },
};
