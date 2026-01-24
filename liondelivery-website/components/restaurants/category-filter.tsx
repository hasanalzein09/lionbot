"use client";

import { useRef } from "react";
import { useLocale, useTranslations } from "next-intl";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils/cn";
import { useCategories } from "@/lib/hooks/use-categories";

interface CategoryFilterProps {
  selectedCategory: string | null;
  onCategoryChange: (category: string | null) => void;
}

export function CategoryFilter({ selectedCategory, onCategoryChange }: CategoryFilterProps) {
  const locale = useLocale();
  const t = useTranslations("restaurants.filters");
  const isRTL = locale === "ar";
  const scrollRef = useRef<HTMLDivElement>(null);

  // Fetch real categories from API
  const { data: apiCategories, isLoading } = useCategories();

  const scroll = (direction: "left" | "right") => {
    if (scrollRef.current) {
      const scrollAmount = 150;
      const actualDirection = isRTL
        ? direction === "left" ? scrollAmount : -scrollAmount
        : direction === "left" ? -scrollAmount : scrollAmount;
      scrollRef.current.scrollBy({
        left: actualDirection,
        behavior: "smooth",
      });
    }
  };

  return (
    <div className="relative">
      {/* Scroll Button - Left */}
      <button
        onClick={() => scroll("left")}
        className={cn(
          "absolute top-1/2 z-10 hidden h-9 w-9 -translate-y-1/2",
          "items-center justify-center rounded-full",
          "bg-white text-gray-600 shadow-md border border-gray-100",
          "hover:bg-gray-50 hover:shadow-lg",
          "transition-all duration-200 md:flex",
          isRTL ? "-right-3" : "-left-3"
        )}
      >
        {isRTL ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </button>

      {/* Scroll Button - Right */}
      <button
        onClick={() => scroll("right")}
        className={cn(
          "absolute top-1/2 z-10 hidden h-9 w-9 -translate-y-1/2",
          "items-center justify-center rounded-full",
          "bg-white text-gray-600 shadow-md border border-gray-100",
          "hover:bg-gray-50 hover:shadow-lg",
          "transition-all duration-200 md:flex",
          isRTL ? "-left-3" : "-right-3"
        )}
      >
        {isRTL ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </button>

      {/* Categories Container */}
      <div
        ref={scrollRef}
        className="scrollbar-hide flex gap-2 overflow-x-auto px-1 py-2"
        style={{ scrollSnapType: "x mandatory" }}
        dir={isRTL ? "rtl" : "ltr"}
      >
        {isLoading ? (
          // Loading skeletons
          Array.from({ length: 8 }).map((_, index) => (
            <div
              key={index}
              className="h-10 w-24 flex-shrink-0 rounded-full skeleton"
            />
          ))
        ) : (
          <>
            {/* "All" option */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onCategoryChange(null)}
              className={cn(
                "flex flex-shrink-0 items-center gap-2 rounded-full px-5 py-2.5",
                "text-sm font-medium transition-all duration-200",
                !selectedCategory
                  ? "bg-emerald-500 text-white shadow-md shadow-emerald-500/25"
                  : "bg-white text-gray-600 border border-gray-200 hover:border-emerald-300 hover:text-emerald-600"
              )}
              style={{ scrollSnapAlign: "start" }}
            >
              <span>{locale === "ar" ? "الكل" : "All"}</span>
            </motion.button>

            {/* API Categories */}
            {apiCategories?.map((category) => {
              const nameAr = category.nameAr || category.name_ar;
              const displayName = locale === "ar" && nameAr ? nameAr : category.name;
              const isSelected = selectedCategory === String(category.id);

              return (
                <motion.button
                  key={category.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => onCategoryChange(String(category.id))}
                  className={cn(
                    "flex flex-shrink-0 items-center gap-2 rounded-full px-5 py-2.5",
                    "text-sm font-medium transition-all duration-200",
                    isSelected
                      ? "bg-emerald-500 text-white shadow-md shadow-emerald-500/25"
                      : "bg-white text-gray-600 border border-gray-200 hover:border-emerald-300 hover:text-emerald-600"
                  )}
                  style={{ scrollSnapAlign: "start" }}
                >
                  {category.icon && <span>{category.icon}</span>}
                  <span>{displayName}</span>
                </motion.button>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
}
