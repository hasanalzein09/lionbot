import { Skeleton } from "@/components/ui/skeleton";

export function RestaurantDetailSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50 pb-28">
      {/* Fixed Header Skeleton */}
      <div className="fixed inset-x-0 top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="container mx-auto px-4">
          <div className="flex h-14 items-center justify-between">
            <Skeleton className="h-10 w-10 rounded-full" />
            <div className="flex items-center gap-2">
              <Skeleton className="h-10 w-10 rounded-full" />
              <Skeleton className="h-10 w-10 rounded-full" />
            </div>
          </div>
        </div>
      </div>

      {/* Hero Image Skeleton */}
      <div className="relative pt-14">
        <Skeleton className="h-56 w-full md:h-72 lg:h-80" />

        {/* White Info Card Skeleton */}
        <div className="container mx-auto px-4">
          <div className="relative -mt-24 rounded-3xl bg-white p-6 shadow-xl shadow-gray-200/50 ring-1 ring-gray-100">
            {/* Status Badges */}
            <div className="mb-4 flex items-center gap-2">
              <Skeleton className="h-7 w-24 rounded-full" />
              <Skeleton className="h-7 w-20 rounded-full" />
            </div>

            {/* Name */}
            <Skeleton className="mb-2 h-8 w-3/4 md:w-1/2" />

            {/* Description */}
            <Skeleton className="mb-4 h-5 w-full max-w-lg" />

            {/* Rating & Delivery Info */}
            <div className="flex flex-wrap items-center gap-4">
              <Skeleton className="h-5 w-32" />
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-5 w-16" />
            </div>

            {/* Divider */}
            <div className="my-5 h-px bg-gray-100" />

            {/* Info Section */}
            <div className="grid gap-4 sm:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-start gap-3">
                  <Skeleton className="h-10 w-10 flex-shrink-0 rounded-xl" />
                  <div className="flex-1">
                    <Skeleton className="mb-1 h-3 w-16" />
                    <Skeleton className="h-5 w-24" />
                  </div>
                </div>
              ))}
            </div>

            {/* Delivery Info Cards */}
            <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="rounded-xl bg-gray-50 p-3">
                  <Skeleton className="mx-auto mb-1 h-5 w-5 rounded" />
                  <Skeleton className="mx-auto mb-1 h-3 w-16" />
                  <Skeleton className="mx-auto h-5 w-12" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Menu Section Skeleton */}
      <div className="container mx-auto px-4 py-8">
        {/* Section Header */}
        <Skeleton className="mb-6 h-7 w-32" />

        {/* Menu Container */}
        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-gray-100">
          {/* Search Bar */}
          <Skeleton className="mb-6 h-12 w-full rounded-xl" />

          {/* Category Nav */}
          <div className="mb-8 flex gap-2 overflow-hidden">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-24 flex-shrink-0 rounded-full" />
            ))}
          </div>

          {/* Menu Items */}
          <div className="space-y-10">
            {Array.from({ length: 2 }).map((_, categoryIndex) => (
              <div key={categoryIndex}>
                <Skeleton className="mb-4 h-6 w-32" />
                <div className="grid gap-4 sm:grid-cols-2">
                  {Array.from({ length: 4 }).map((_, itemIndex) => (
                    <div
                      key={itemIndex}
                      className="flex gap-4 rounded-2xl bg-gray-50 p-4"
                    >
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-5 w-3/4" />
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-5 w-20" />
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
    </div>
  );
}
