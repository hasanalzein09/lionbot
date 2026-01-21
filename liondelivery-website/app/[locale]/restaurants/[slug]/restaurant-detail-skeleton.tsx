import { Skeleton } from "@/components/ui/skeleton";

export function RestaurantDetailSkeleton() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Skeleton */}
      <div className="relative">
        <Skeleton className="h-48 w-full md:h-64" />

        <div className="container mx-auto px-4">
          <div className="relative -mt-20">
            <div className="rounded-2xl bg-secondary-800 p-6">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="flex-1 space-y-3">
                  <Skeleton className="h-6 w-24" />
                  <Skeleton className="h-8 w-48" />
                  <Skeleton className="h-4 w-full max-w-md" />
                  <div className="flex gap-4">
                    <Skeleton className="h-5 w-16" />
                    <Skeleton className="h-5 w-20" />
                    <Skeleton className="h-5 w-12" />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Skeleton className="h-10 w-10 rounded-xl" />
                  <Skeleton className="h-10 w-10 rounded-xl" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Menu Skeleton */}
      <div className="container mx-auto px-4 py-8">
        {/* Breadcrumbs */}
        <Skeleton className="mb-6 h-5 w-48" />

        {/* Search Bar */}
        <Skeleton className="mb-4 h-12 w-full rounded-xl" />

        {/* Category Nav */}
        <div className="mb-6 flex gap-2 overflow-hidden">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-24 flex-shrink-0 rounded-full" />
          ))}
        </div>

        {/* Menu Items */}
        <div className="space-y-8">
          {Array.from({ length: 2 }).map((_, categoryIndex) => (
            <div key={categoryIndex}>
              <Skeleton className="mb-4 h-7 w-32" />
              <div className="grid gap-4 sm:grid-cols-2">
                {Array.from({ length: 4 }).map((_, itemIndex) => (
                  <div
                    key={itemIndex}
                    className="flex gap-4 rounded-2xl bg-secondary-800 p-4"
                  >
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-5 w-3/4" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-5 w-16" />
                    </div>
                    <Skeleton className="h-24 w-24 flex-shrink-0 rounded-xl" />
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
