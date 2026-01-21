"use client";

import { RestaurantCard } from "./restaurant-card";
import { RestaurantSkeleton } from "./restaurant-skeleton";
import type { Restaurant } from "@/types/restaurant";

interface RestaurantGridProps {
  restaurants: Restaurant[];
  isLoading?: boolean;
  skeletonCount?: number;
}

export function RestaurantGrid({
  restaurants,
  isLoading = false,
  skeletonCount = 8
}: RestaurantGridProps) {
  if (isLoading) {
    return (
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {Array.from({ length: skeletonCount }).map((_, i) => (
          <RestaurantSkeleton key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {restaurants.map((restaurant, index) => (
        <RestaurantCard
          key={restaurant.id}
          restaurant={restaurant}
          index={index}
        />
      ))}
    </div>
  );
}
