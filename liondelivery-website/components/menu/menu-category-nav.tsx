"use client";

import { useRef, useEffect, useState } from "react";
import { useLocale } from "next-intl";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import type { MenuCategory } from "@/types/menu";

interface MenuCategoryNavProps {
  categories: MenuCategory[];
  activeCategory: string | number;
  onCategoryClick: (categoryId: string | number) => void;
}

export function MenuCategoryNav({
  categories,
  activeCategory,
  onCategoryClick,
}: MenuCategoryNavProps) {
  const locale = useLocale();
  const isRTL = locale === "ar";
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(false);

  const checkArrows = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      const scrollStart = isRTL ? scrollWidth - clientWidth + scrollLeft : scrollLeft;
      const scrollEnd = isRTL ? -scrollLeft : scrollWidth - clientWidth - scrollLeft;

      setShowLeftArrow(Math.abs(scrollStart) > 1);
      setShowRightArrow(scrollEnd > 1);
    }
  };

  useEffect(() => {
    checkArrows();
    window.addEventListener("resize", checkArrows);
    return () => window.removeEventListener("resize", checkArrows);
  }, [categories]);

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

  const handleCategoryClick = (categoryId: string | number) => {
    onCategoryClick(categoryId);

    // Scroll the element into view
    const element = document.getElementById(`category-${categoryId}`);
    if (element) {
      const headerOffset = 150;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth",
      });
    }
  };

  return (
    <div className={cn(
      "sticky top-16 z-30 -mx-4 px-4 py-3",
      "bg-white/95 backdrop-blur-md",
      "border-b border-gray-100",
      "shadow-sm"
    )}>
      <div className="relative">
        {/* Left Arrow */}
        {showLeftArrow && (
          <button
            onClick={() => scroll("left")}
            className={cn(
              "absolute top-1/2 z-10 -translate-y-1/2",
              "flex h-8 w-8 items-center justify-center rounded-full",
              "bg-white text-gray-600 shadow-md",
              "transition-all hover:bg-gray-50 hover:shadow-lg",
              "border border-gray-100",
              isRTL ? "-right-1" : "-left-1"
            )}
          >
            {isRTL ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </button>
        )}

        {/* Right Arrow */}
        {showRightArrow && (
          <button
            onClick={() => scroll("right")}
            className={cn(
              "absolute top-1/2 z-10 -translate-y-1/2",
              "flex h-8 w-8 items-center justify-center rounded-full",
              "bg-white text-gray-600 shadow-md",
              "transition-all hover:bg-gray-50 hover:shadow-lg",
              "border border-gray-100",
              isRTL ? "-left-1" : "-right-1"
            )}
          >
            {isRTL ? (
              <ChevronLeft className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </button>
        )}

        {/* Categories */}
        <div
          ref={scrollRef}
          onScroll={checkArrows}
          className="scrollbar-hide flex gap-2 overflow-x-auto px-1"
        >
          {categories.map((category) => {
            const nameAr = category.nameAr || category.name_ar;
            const displayName = locale === "ar" && nameAr ? nameAr : category.name;
            const isActive = String(activeCategory) === String(category.id);

            return (
              <button
                key={category.id}
                onClick={() => handleCategoryClick(category.id)}
                className={cn(
                  "relative flex-shrink-0 px-4 py-2 text-sm font-medium transition-all whitespace-nowrap rounded-full",
                  isActive
                    ? "text-emerald-600 bg-emerald-50"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                )}
              >
                {displayName}
                {category.itemCount !== undefined && category.itemCount > 0 && (
                  <span className={cn(
                    "text-xs opacity-70",
                    isRTL ? "mr-1.5" : "ml-1.5"
                  )}>
                    ({category.itemCount})
                  </span>
                )}
                {/* Active Underline */}
                {isActive && (
                  <span className="absolute bottom-0 left-1/2 -translate-x-1/2 h-0.5 w-8 bg-emerald-500 rounded-full" />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
