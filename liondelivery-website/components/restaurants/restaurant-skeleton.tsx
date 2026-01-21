import { Skeleton } from "@/components/ui/skeleton";

export function RestaurantSkeleton() {
  return (
    <div className="overflow-hidden rounded-2xl bg-secondary-800">
      {/* Image Skeleton */}
      <Skeleton className="aspect-[16/10] w-full" />

      {/* Content */}
      <div className="p-4 space-y-3">
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1">
            <Skeleton className="h-5 w-3/4" />
            <Skeleton className="h-4 w-1/4" />
          </div>
          <Skeleton className="h-7 w-14 rounded-lg" />
        </div>

        <div className="flex items-center gap-4">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-16" />
        </div>
      </div>
    </div>
  );
}
