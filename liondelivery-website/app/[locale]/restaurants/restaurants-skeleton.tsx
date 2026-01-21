import { Skeleton } from "@/components/ui/skeleton";
import { RestaurantSkeleton } from "@/components/restaurants/restaurant-skeleton";

export function RestaurantsSkeleton() {
  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4">
        {/* Header Skeleton */}
        <div className="mb-8">
          <Skeleton className="mb-2 h-10 w-48" />
          <Skeleton className="h-5 w-64" />
        </div>

        {/* Search Bar Skeleton */}
        <div className="mb-6">
          <Skeleton className="h-12 w-full rounded-xl" />
        </div>

        {/* Category Filter Skeleton */}
        <div className="mb-6 flex gap-2 overflow-hidden">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-24 flex-shrink-0 rounded-full" />
          ))}
        </div>

        {/* Results Count & Sort Skeleton */}
        <div className="mb-6 flex items-center justify-between">
          <Skeleton className="h-5 w-24" />
          <Skeleton className="h-10 w-32 rounded-xl" />
        </div>

        {/* Restaurant Grid Skeleton */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <RestaurantSkeleton key={i} />
          ))}
        </div>
      </div>
    </div>
  );
}
