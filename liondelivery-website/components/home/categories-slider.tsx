"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useRef } from "react";

const categories = [
  { id: "all", nameAr: "الكل", nameEn: "All", icon: "🍽️" },
  { id: "burger", nameAr: "برغر", nameEn: "Burger", icon: "🍔" },
  { id: "shawarma", nameAr: "شاورما", nameEn: "Shawarma", icon: "🥙" },
  { id: "pizza", nameAr: "بيتزا", nameEn: "Pizza", icon: "🍕" },
  { id: "coffee", nameAr: "قهوة", nameEn: "Coffee", icon: "☕" },
  { id: "sweets", nameAr: "حلويات", nameEn: "Sweets", icon: "🍰" },
  { id: "juice", nameAr: "عصائر", nameEn: "Juice", icon: "🥤" },
  { id: "chicken", nameAr: "دجاج", nameEn: "Chicken", icon: "🍗" },
  { id: "seafood", nameAr: "مأكولات بحرية", nameEn: "Seafood", icon: "🦐" },
  { id: "grills", nameAr: "مشاوي", nameEn: "Grills", icon: "🥩" },
];

export function CategoriesSlider() {
  const t = useTranslations("home.categories");
  const locale = useLocale();
  const scrollRef = useRef<HTMLDivElement>(null);

  const scroll = (direction: "left" | "right") => {
    if (scrollRef.current) {
      const scrollAmount = 200;
      scrollRef.current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      });
    }
  };

  return (
    <section className="py-12">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <motion.h2
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="text-2xl font-bold md:text-3xl"
          >
            {t("title")}
          </motion.h2>

          {/* Scroll Buttons */}
          <div className="hidden gap-2 md:flex">
            <button
              onClick={() => scroll("left")}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-800 text-foreground transition-colors hover:bg-secondary-700"
            >
              {locale === "ar" ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
            </button>
            <button
              onClick={() => scroll("right")}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-800 text-foreground transition-colors hover:bg-secondary-700"
            >
              {locale === "ar" ? <ChevronLeft className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Categories */}
        <div
          ref={scrollRef}
          className="scrollbar-hide flex gap-4 overflow-x-auto pb-4"
          style={{ scrollSnapType: "x mandatory" }}
        >
          {categories.map((category, index) => (
            <motion.div
              key={category.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
              style={{ scrollSnapAlign: "start" }}
            >
              <Link
                href={
                  category.id === "all"
                    ? `/${locale}/restaurants`
                    : `/${locale}/restaurants?category=${category.id}`
                }
                className="group flex flex-col items-center gap-3"
              >
                <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-secondary-800 text-4xl transition-all group-hover:scale-110 group-hover:bg-primary-500/20 group-hover:shadow-lg group-hover:shadow-primary-500/10">
                  {category.icon}
                </div>
                <span className="text-sm font-medium text-muted-foreground transition-colors group-hover:text-primary-500">
                  {locale === "ar" ? category.nameAr : category.nameEn}
                </span>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
