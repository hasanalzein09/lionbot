import { get } from "./client";

// Using /public endpoints - no authentication required
const PUBLIC_PREFIX = "/public";

export interface Category {
  id: string;
  name: string;
  nameAr?: string;
  name_ar?: string;
  slug: string;
  icon?: string;
  image?: string;
  description?: string;
  descriptionAr?: string;
  restaurantCount?: number;
  sortOrder?: number;
}

export const categoriesApi = {
  /**
   * Get all restaurant categories
   */
  getAll: async (): Promise<Category[]> => {
    const response = await get<Category[]>(`${PUBLIC_PREFIX}/categories/`);
    return response.map((cat) => ({
      ...cat,
      nameAr: cat.name_ar,
    }));
  },

  /**
   * Get a single category by slug
   */
  getBySlug: async (slug: string): Promise<Category> => {
    const categories = await categoriesApi.getAll();
    const category = categories.find((c) => c.slug === slug);
    if (!category) {
      throw new Error("Category not found");
    }
    return category;
  },

  /**
   * Get popular categories
   */
  getPopular: async (limit = 8): Promise<Category[]> => {
    const categories = await categoriesApi.getAll();
    return categories.slice(0, limit);
  },
};
