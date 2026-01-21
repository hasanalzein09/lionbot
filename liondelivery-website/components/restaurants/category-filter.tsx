"use client";

import { useRef } from "react";
import { useLocale, useTranslations } from "next-intl";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils/cn";

const categories = [
  { id: "all", nameAr: "الكل", nameEn: "All", icon: "🍽️" },
  { id: "burger", nameAr: "برغر", nameEn: "Burger", icon: "🍔" },
  { id: "shawarma", nameAr: "شاورما", nameEn: "Shawarma", icon: "🥙" },
  { id: "pizza", nameAr: "بيتزا", nameEn: "Pizza", icon: "🍕" },
  { id: "coffee", nameAr: "قهوة", nameEn: "Coffee", icon: "☕" },
  { id: "sweets", nameAr: "حلويات", nameEn: "Sweets", icon: "🍰" },
  { id: "juice", nameAr: "عصائر", nameEn: "Juice", icon: "🥤" },
  { id: "chicken", nameAr: "دجاج", nameEn: "Chicken", icon: "🍗" },
  { id: "seafood", nameAr: "بحري", nameEn: "Seafood", icon: "🦐" },
  { id: "grills", nameAr: "مشاوي", nameEn: "Grills", icon: "🥩" },
  { id: "sandwich", nameAr: "ساندويش", nameEn: "Sandwich", icon: "🥪" },
  { id: "salad", nameAr: "سلطة", nameEn: "Salad", icon: "🥗" },
];

interface CategoryFilterProps {
  selectedCategory: string | null;
  onCategoryChange: (category: string | null) => void;
}

export function CategoryFilter({ selectedCategory, onCategoryChange }: CategoryFilterProps) {
  const locale = useLocale();
  const t = useTranslations("restaurants.filters");
  const scrollRef = useRef<HTMLDivElement>(null);

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
        {categories.map((category) => {
          const isSelected =
            (category.id === "all" && !selectedCategory) ||
            selectedCategory === category.id;

          return (
            <button
              key={category.id}
              onClick={() => onCategoryChange(category.id === "all" ? null : category.id)}
              className={cn(
                "flex flex-shrink-0 items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-all",
                "scroll-snap-align-start",
                isSelected
                  ? "bg-primary-500 text-white shadow-lg shadow-primary-500/25"
                  : "bg-secondary-800 text-muted-foreground hover:bg-secondary-700 hover:text-foreground"
              )}
              style={{ scrollSnapAlign: "start" }}
            >
              <span>{category.icon}</span>
              <span>{locale === "ar" ? category.nameAr : category.nameEn}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
