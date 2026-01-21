"use client";

import { useQuery } from "@tanstack/react-query";
import { searchApi } from "@/lib/api/search";

export const searchKeys = {
  all: ["search"] as const,
  query: (q: string) => [...searchKeys.all, q] as const,
  suggestions: (q: string) => [...searchKeys.all, "suggestions", q] as const,
  restaurants: (q: string) => [...searchKeys.all, "restaurants", q] as const,
  items: (q: string) => [...searchKeys.all, "items", q] as const,
  popular: () => [...searchKeys.all, "popular"] as const,
};

/**
 * Hook for global search
 */
export function useSearch(query: string) {
  return useQuery({
    queryKey: searchKeys.query(query),
    queryFn: () => searchApi.search(query),
    enabled: query.length >= 2,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook for search suggestions (autocomplete)
 */
export function useSearchSuggestions(query: string) {
  return useQuery({
    queryKey: searchKeys.suggestions(query),
    queryFn: () => searchApi.getSuggestions(query),
    enabled: query.length >= 2,
    staleTime: 60 * 1000, // 1 minute
  });
}

/**
 * Hook to search restaurants only
 */
export function useSearchRestaurantsOnly(query: string) {
  return useQuery({
    queryKey: searchKeys.restaurants(query),
    queryFn: () => searchApi.searchRestaurants(query),
    enabled: query.length >= 2,
  });
}

/**
 * Hook to search items only
 */
export function useSearchItemsOnly(query: string) {
  return useQuery({
    queryKey: searchKeys.items(query),
    queryFn: () => searchApi.searchItems(query),
    enabled: query.length >= 2,
  });
}

/**
 * Hook to get popular searches
 */
export function usePopularSearches() {
  return useQuery({
    queryKey: searchKeys.popular(),
    queryFn: () => searchApi.getPopular(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}
