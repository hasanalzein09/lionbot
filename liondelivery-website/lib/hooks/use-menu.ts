"use client";

import { useQuery } from "@tanstack/react-query";
import { menusApi } from "@/lib/api/menus";

export const menuKeys = {
  all: ["menus"] as const,
  byRestaurant: (restaurantId: string) =>
    [...menuKeys.all, restaurantId] as const,
  categories: (restaurantId: string) =>
    [...menuKeys.byRestaurant(restaurantId), "categories"] as const,
  items: (restaurantId: string, categoryId: string) =>
    [...menuKeys.byRestaurant(restaurantId), "items", categoryId] as const,
  item: (restaurantId: string, itemId: string) =>
    [...menuKeys.byRestaurant(restaurantId), "item", itemId] as const,
  popular: (restaurantId: string) =>
    [...menuKeys.byRestaurant(restaurantId), "popular"] as const,
  search: (restaurantId: string, query: string) =>
    [...menuKeys.byRestaurant(restaurantId), "search", query] as const,
};

/**
 * Hook to fetch menu for a restaurant
 * Uses public API - no authentication required
 */
export function useMenu(restaurantId: string) {
  return useQuery({
    queryKey: menuKeys.byRestaurant(restaurantId),
    queryFn: () => menusApi.getByRestaurant(restaurantId),
    enabled: !!restaurantId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch menu categories for a restaurant
 */
export function useMenuCategories(restaurantId: string) {
  return useQuery({
    queryKey: menuKeys.categories(restaurantId),
    queryFn: () => menusApi.getCategories(restaurantId),
    enabled: !!restaurantId,
  });
}

/**
 * Hook to fetch items for a specific category
 */
export function useMenuItems(restaurantId: string, categoryId: string) {
  return useQuery({
    queryKey: menuKeys.items(restaurantId, categoryId),
    queryFn: () => menusApi.getItemsByCategory(restaurantId, categoryId),
    enabled: !!restaurantId && !!categoryId,
  });
}

/**
 * Hook to fetch a single menu item
 */
export function useMenuItem(restaurantId: string, itemId: string) {
  return useQuery({
    queryKey: menuKeys.item(restaurantId, itemId),
    queryFn: () => menusApi.getItem(restaurantId, itemId),
    enabled: !!restaurantId && !!itemId,
  });
}

/**
 * Hook to fetch popular items for a restaurant
 */
export function usePopularItems(restaurantId: string, limit = 5) {
  return useQuery({
    queryKey: menuKeys.popular(restaurantId),
    queryFn: () => menusApi.getPopularItems(restaurantId, limit),
    enabled: !!restaurantId,
  });
}

/**
 * Hook to search menu items
 */
export function useSearchMenu(restaurantId: string, query: string) {
  return useQuery({
    queryKey: menuKeys.search(restaurantId, query),
    queryFn: () => menusApi.search(restaurantId, query),
    enabled: !!restaurantId && query.length >= 2,
  });
}
