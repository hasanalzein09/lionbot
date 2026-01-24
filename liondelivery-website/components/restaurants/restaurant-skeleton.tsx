export function RestaurantSkeleton() {
  return (
    <div className="overflow-hidden rounded-2xl bg-white shadow-sm border border-gray-100">
      {/* Image Skeleton */}
      <div className="aspect-[16/10] w-full skeleton" />

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Title and Rating */}
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-2 flex-1">
            <div className="h-5 w-3/4 skeleton rounded-md" />
            <div className="h-4 w-1/4 skeleton rounded-md" />
          </div>
          <div className="h-7 w-14 skeleton rounded-lg flex-shrink-0" />
        </div>

        {/* Meta Info */}
        <div className="flex items-center gap-4">
          <div className="h-4 w-20 skeleton rounded-md" />
          <div className="h-4 w-16 skeleton rounded-md" />
        </div>

        {/* Delivery Fee */}
        <div className="pt-2 border-t border-gray-100">
          <div className="h-3 w-24 skeleton rounded-md" />
        </div>
      </div>
    </div>
  );
}
