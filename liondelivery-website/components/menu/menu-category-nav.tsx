"use client";

import { useRef, useEffect, useState } from "react";
import { useLocale } from "next-intl";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import type { MenuCategory } from "@/types/menu";

interface MenuCategoryNavProps {
  categories: MenuCategory[];
  activeCategory: string;
  onCategoryClick: (categoryId: string) => void;
}

export function MenuCategoryNav({
  categories,
  activeCategory,
  onCategoryClick,
}: MenuCategoryNavProps) {
  const locale = useLocale();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(false);

  const checkArrows = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setShowLeftArrow(scrollLeft > 0);
      setShowRightArrow(scrollLeft + clientWidth < scrollWidth - 1);
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
      scrollRef.current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      });
    }
  };

  const handleCategoryClick = (categoryId: string) => {
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
    <div className="sticky top-16 z-30 -mx-4 bg-background/95 backdrop-blur-lg px-4 py-3 border-b border-border">
      <div className="relative">
        {/* Left Arrow */}
        {showLeftArrow && (
          <button
            onClick={() => scroll("left")}
            className="absolute -left-1 top-1/2 z-10 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full bg-secondary-800 text-foreground shadow-lg transition-colors hover:bg-secondary-700"
          >
            {locale === "ar" ? (
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
            className="absolute -right-1 top-1/2 z-10 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full bg-secondary-800 text-foreground shadow-lg transition-colors hover:bg-secondary-700"
          >
            {locale === "ar" ? (
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
            const displayName =
              locale === "ar" && category.nameAr ? category.nameAr : category.name;
            const isActive = activeCategory === category.id;

            return (
              <button
                key={category.id}
                onClick={() => handleCategoryClick(category.id)}
                className={cn(
                  "flex-shrink-0 rounded-full px-4 py-2 text-sm font-medium transition-all whitespace-nowrap",
                  isActive
                    ? "bg-primary-500 text-white shadow-lg shadow-primary-500/25"
                    : "bg-secondary-800 text-muted-foreground hover:bg-secondary-700 hover:text-foreground"
                )}
              >
                {displayName}
                {category.itemCount && (
                  <span className="ml-1.5 text-xs opacity-70">
                    ({category.itemCount})
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
