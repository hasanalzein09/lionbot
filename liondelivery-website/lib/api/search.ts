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
   * Uses public API - no authentication required
   */
  search: async (query: string, limit = 20): Promise<SearchResults> => {
    const response = await get<SearchResults>("/public/search/", {
      q: query,
      limit,
    });
    return {
      restaurants: response.restaurants || [],
      items: response.items || [],
      total: (response.restaurants?.length || 0) + (response.items?.length || 0),
    };
  },

  /**
   * Get search suggestions (autocomplete)
   * Note: This endpoint doesn't exist in backend yet, using search as fallback
   */
  getSuggestions: async (query: string, limit = 8): Promise<SearchSuggestion[]> => {
    try {
      const response = await get<SearchResults>("/public/search/", {
        q: query,
        limit,
      });
      // Convert search results to suggestions format
      const suggestions: SearchSuggestion[] = [];
      response.restaurants?.forEach(r => {
        suggestions.push({
          type: "restaurant",
          id: String(r.id),
          name: r.name,
          nameAr: r.name_ar,
          image: r.image,
        });
      });
      return suggestions.slice(0, limit);
    } catch {
      return [];
    }
  },

  /**
   * Search restaurants only
   */
  searchRestaurants: async (query: string, limit = 10): Promise<Restaurant[]> => {
    const response = await get<SearchResults>("/public/search/", {
      q: query,
      limit,
    });
    return response.restaurants || [];
  },

  /**
   * Search menu items only
   */
  searchItems: async (query: string, limit = 10): Promise<MenuItem[]> => {
    const response = await get<SearchResults>("/public/search/", {
      q: query,
      limit,
    });
    return response.items || [];
  },

  /**
   * Get popular searches
   * Note: Using static list for now
   */
  getPopular: async (): Promise<string[]> => {
    return ["Burger", "Shawarma", "Pizza", "Coffee", "Sweets"];
  },
};
