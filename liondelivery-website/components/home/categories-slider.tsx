"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useRef, useState, useEffect } from "react";
import { useCategories } from "@/lib/hooks/use-categories";
import { Skeleton } from "@/components/ui/skeleton";

// Emoji background colors for visual variety
const emojiColors = [
  "bg-emerald-100",
  "bg-rose-100",
  "bg-amber-100",
  "bg-sky-100",
  "bg-violet-100",
  "bg-orange-100",
  "bg-pink-100",
  "bg-teal-100",
];

export function CategoriesSlider() {
  const t = useTranslations("home.categories");
  const locale = useLocale();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [showLeftFade, setShowLeftFade] = useState(false);
  const [showRightFade, setShowRightFade] = useState(true);

  // Fetch real categories from API
  const { data: apiCategories, isLoading } = useCategories();

  const scroll = (direction: "left" | "right") => {
    if (scrollRef.current) {
      const scrollAmount = 250;
      scrollRef.current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      });
    }
  };

  const handleScroll = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setShowLeftFade(scrollLeft > 10);
      setShowRightFade(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  useEffect(() => {
    const ref = scrollRef.current;
    if (ref) {
      ref.addEventListener("scroll", handleScroll);
      handleScroll();
      return () => ref.removeEventListener("scroll", handleScroll);
    }
  }, []);

  return (
    <section className="bg-white py-12 md:py-16">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-2xl font-bold text-gray-900 md:text-3xl">
              {t("title")}
            </h2>
            <p className="mt-1 text-gray-500">
              {locale === "ar" ? "اختر نوع طعامك المفضل" : "Choose your favorite cuisine"}
            </p>
          </motion.div>

          {/* Scroll Buttons */}
          <div className="hidden gap-2 md:flex">
            <button
              onClick={() => scroll("left")}
              disabled={!showLeftFade}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-gray-700 shadow-md ring-1 ring-gray-100 transition-all hover:bg-emerald-50 hover:text-emerald-600 hover:shadow-lg disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {locale === "ar" ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
            </button>
            <button
              onClick={() => scroll("right")}
              disabled={!showRightFade}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-gray-700 shadow-md ring-1 ring-gray-100 transition-all hover:bg-emerald-50 hover:text-emerald-600 hover:shadow-lg disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {locale === "ar" ? <ChevronLeft className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Categories with Fade Edges */}
        <div className="relative">
          {/* Left Fade */}
          <div
            className={`pointer-events-none absolute start-0 top-0 z-10 h-full w-16 bg-gradient-to-e from-white to-transparent transition-opacity duration-300 ${
              showLeftFade ? "opacity-100" : "opacity-0"
            }`}
          />

          {/* Right Fade */}
          <div
            className={`pointer-events-none absolute end-0 top-0 z-10 h-full w-16 bg-gradient-to-s from-white to-transparent transition-opacity duration-300 ${
              showRightFade ? "opacity-100" : "opacity-0"
            }`}
          />

          <div
            ref={scrollRef}
            className="scrollbar-hide flex gap-4 overflow-x-auto pb-4"
            style={{ scrollSnapType: "x mandatory" }}
          >
            {isLoading ? (
              // Loading skeletons
              Array.from({ length: 8 }).map((_, index) => (
                <div key={index} className="flex flex-col items-center gap-3">
                  <Skeleton className="h-24 w-24 rounded-2xl" />
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
                    <div className="relative flex h-24 w-24 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-100 to-teal-100 text-5xl shadow-md ring-1 ring-gray-100 transition-all duration-300 group-hover:-translate-y-2 group-hover:shadow-xl group-hover:shadow-emerald-500/20">
                      <span className="transition-transform duration-300 group-hover:scale-110">
                        🍽️
                      </span>
                    </div>
                    <span className="text-sm font-semibold text-gray-700 transition-colors group-hover:text-emerald-600">
                      {locale === "ar" ? "الكل" : "All"}
                    </span>
                  </Link>
                </motion.div>

                {/* API Categories */}
                {apiCategories?.map((category, index) => {
                  const nameAr = category.nameAr || category.name_ar;
                  const displayName = locale === "ar" && nameAr ? nameAr : category.name;
                  const bgColor = emojiColors[index % emojiColors.length];

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
                        <div className={`relative flex h-24 w-24 items-center justify-center rounded-2xl ${bgColor} text-5xl shadow-md ring-1 ring-gray-100 transition-all duration-300 group-hover:-translate-y-2 group-hover:shadow-xl group-hover:shadow-emerald-500/20`}>
                          <span className="transition-transform duration-300 group-hover:scale-110">
                            {category.icon || "🍽️"}
                          </span>
                        </div>
                        <span className="text-sm font-semibold text-gray-700 transition-colors group-hover:text-emerald-600">
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
      </div>
    </section>
  );
}
