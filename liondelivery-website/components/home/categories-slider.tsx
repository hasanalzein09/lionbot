"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useRef } from "react";
import { useCategories } from "@/lib/hooks/use-categories";
import { Skeleton } from "@/components/ui/skeleton";

export function CategoriesSlider() {
  const t = useTranslations("home.categories");
  const locale = useLocale();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Fetch real categories from API
  const { data: apiCategories, isLoading } = useCategories();

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
          {isLoading ? (
            // Loading skeletons
            Array.from({ length: 8 }).map((_, index) => (
              <div key={index} className="flex flex-col items-center gap-3">
                <Skeleton className="h-20 w-20 rounded-2xl" />
                <Skeleton className="h-4 w-16" />
              </div>
            ))
          ) : (
            <>
              {/* "All" category */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                style={{ scrollSnapAlign: "start" }}
              >
                <Link
                  href={`/${locale}/restaurants`}
                  className="group flex flex-col items-center gap-3"
                >
                  <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-secondary-800 text-4xl transition-all group-hover:scale-110 group-hover:bg-primary-500/20 group-hover:shadow-lg group-hover:shadow-primary-500/10">
                    🍽️
                  </div>
                  <span className="text-sm font-medium text-muted-foreground transition-colors group-hover:text-primary-500">
                    {locale === "ar" ? "الكل" : "All"}
                  </span>
                </Link>
              </motion.div>

              {/* API Categories */}
              {apiCategories?.map((category, index) => {
                const nameAr = category.nameAr || category.name_ar;
                const displayName = locale === "ar" && nameAr ? nameAr : category.name;

                return (
                  <motion.div
                    key={category.id}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: (index + 1) * 0.05 }}
                    style={{ scrollSnapAlign: "start" }}
                  >
                    <Link
                      href={`/${locale}/restaurants?category=${category.id}`}
                      className="group flex flex-col items-center gap-3"
                    >
                      <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-secondary-800 text-4xl transition-all group-hover:scale-110 group-hover:bg-primary-500/20 group-hover:shadow-lg group-hover:shadow-primary-500/10">
                        {category.icon || "🍽️"}
                      </div>
                      <span className="text-sm font-medium text-muted-foreground transition-colors group-hover:text-primary-500">
                        {displayName}
                      </span>
                    </Link>
                  </motion.div>
                );
              })}
            </>
          )}
        </div>
      </div>
    </section>
  );
}
