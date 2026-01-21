"use client";

import { useQuery } from "@tanstack/react-query";
import { categoriesApi, type Category } from "@/lib/api/categories";

export const categoryKeys = {
  all: ["categories"] as const,
  lists: () => [...categoryKeys.all, "list"] as const,
  popular: () => [...categoryKeys.all, "popular"] as const,
  detail: (slug: string) => [...categoryKeys.all, slug] as const,
};

/**
 * Hook to fetch all categories
 */
export function useCategories() {
  return useQuery({
    queryKey: categoryKeys.lists(),
    queryFn: () => categoriesApi.getAll(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to fetch popular categories
 */
export function usePopularCategories(limit = 8) {
  return useQuery({
    queryKey: categoryKeys.popular(),
    queryFn: () => categoriesApi.getPopular(limit),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to fetch a single category by slug
 */
export function useCategory(slug: string) {
  return useQuery({
    queryKey: categoryKeys.detail(slug),
    queryFn: () => categoriesApi.getBySlug(slug),
    enabled: !!slug,
  });
}
