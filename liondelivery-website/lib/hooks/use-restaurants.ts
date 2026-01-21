"use client";

import { useQuery, useInfiniteQuery } from "@tanstack/react-query";
import { restaurantsApi } from "@/lib/api/restaurants";
import type { RestaurantFilters } from "@/types/restaurant";

export const restaurantKeys = {
  all: ["restaurants"] as const,
  lists: () => [...restaurantKeys.all, "list"] as const,
  list: (filters?: RestaurantFilters) =>
    [...restaurantKeys.lists(), filters] as const,
  featured: () => [...restaurantKeys.all, "featured"] as const,
  details: () => [...restaurantKeys.all, "detail"] as const,
  detail: (slug: string) => [...restaurantKeys.details(), slug] as const,
};

/**
 * Hook to fetch all restaurants with optional filters
 * Uses public API - no authentication required
 */
export function useRestaurants(filters?: RestaurantFilters) {
  return useQuery({
    queryKey: restaurantKeys.list(filters),
    queryFn: () => restaurantsApi.getAll(filters),
  });
}

/**
 * Hook to fetch restaurants with infinite scroll
 * Uses public API - no authentication required
 */
export function useInfiniteRestaurants(filters?: Omit<RestaurantFilters, "page">) {
  return useInfiniteQuery({
    queryKey: [...restaurantKeys.list(filters), "infinite"],
    queryFn: ({ pageParam = 1 }) =>
      restaurantsApi.getAll({ ...filters, page: pageParam }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) =>
      lastPage.hasMore ? lastPage.page + 1 : undefined,
  });
}

/**
 * Hook to fetch featured restaurants
 * Uses public API - no authentication required
 */
export function useFeaturedRestaurants(limit = 6) {
  return useQuery({
    queryKey: restaurantKeys.featured(),
    queryFn: () => restaurantsApi.getFeatured(limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch a single restaurant by slug
 * Uses public API - no authentication required
 */
export function useRestaurant(slug: string) {
  return useQuery({
    queryKey: restaurantKeys.detail(slug),
    queryFn: () => restaurantsApi.getBySlug(slug),
    enabled: !!slug,
  });
}

/**
 * Hook to search restaurants
 * Uses public API - no authentication required
 */
export function useSearchRestaurants(query: string) {
  return useQuery({
    queryKey: ["restaurants", "search", query],
    queryFn: () => restaurantsApi.search(query),
    enabled: query.length >= 2,
  });
}
