"use client";

import { useRef } from "react";
import { useLocale, useTranslations } from "next-intl";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { useCategories } from "@/lib/hooks/use-categories";
import { Skeleton } from "@/components/ui/skeleton";

interface CategoryFilterProps {
  selectedCategory: string | null;
  onCategoryChange: (category: string | null) => void;
}

export function CategoryFilter({ selectedCategory, onCategoryChange }: CategoryFilterProps) {
  const locale = useLocale();
  const t = useTranslations("restaurants.filters");
  const scrollRef = useRef<HTMLDivElement>(null);

  // Fetch real categories from API
  const { data: apiCategories, isLoading } = useCategories();

  const scroll = (direction: "left" | "right") => {
    if (scrollRef.current) {
      const scrollAmount = 150;
      scrollRef.current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      });
    }
  };

  return (
    <div className="relative">
      {/* Scroll Buttons */}
      <button
        onClick={() => scroll("left")}
        className="absolute -left-2 top-1/2 z-10 hidden h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full bg-secondary-800 text-foreground shadow-lg transition-colors hover:bg-secondary-700 md:flex"
      >
        {locale === "ar" ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </button>
      <button
        onClick={() => scroll("right")}
        className="absolute -right-2 top-1/2 z-10 hidden h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full bg-secondary-800 text-foreground shadow-lg transition-colors hover:bg-secondary-700 md:flex"
      >
        {locale === "ar" ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </button>

      {/* Categories */}
      <div
        ref={scrollRef}
        className="scrollbar-hide flex gap-2 overflow-x-auto px-1 py-2"
        style={{ scrollSnapType: "x mandatory" }}
      >
        {isLoading ? (
          // Loading skeletons
          Array.from({ length: 8 }).map((_, index) => (
            <Skeleton key={index} className="h-10 w-24 flex-shrink-0 rounded-full" />
          ))
        ) : (
          <>
            {/* "All" option */}
            <button
              onClick={() => onCategoryChange(null)}
              className={cn(
                "flex flex-shrink-0 items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-all",
                "scroll-snap-align-start",
                !selectedCategory
                  ? "bg-primary-500 text-white shadow-lg shadow-primary-500/25"
                  : "bg-secondary-800 text-muted-foreground hover:bg-secondary-700 hover:text-foreground"
              )}
              style={{ scrollSnapAlign: "start" }}
            >
              <span>🍽️</span>
              <span>{locale === "ar" ? "الكل" : "All"}</span>
            </button>

            {/* API Categories */}
            {apiCategories?.map((category) => {
              const nameAr = category.nameAr || category.name_ar;
              const displayName = locale === "ar" && nameAr ? nameAr : category.name;
              const isSelected = selectedCategory === String(category.id);

              return (
                <button
                  key={category.id}
                  onClick={() => onCategoryChange(String(category.id))}
                  className={cn(
                    "flex flex-shrink-0 items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-all",
                    "scroll-snap-align-start",
                    isSelected
                      ? "bg-primary-500 text-white shadow-lg shadow-primary-500/25"
                      : "bg-secondary-800 text-muted-foreground hover:bg-secondary-700 hover:text-foreground"
                  )}
                  style={{ scrollSnapAlign: "start" }}
                >
                  <span>{category.icon || "🍽️"}</span>
                  <span>{displayName}</span>
                </button>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
}
