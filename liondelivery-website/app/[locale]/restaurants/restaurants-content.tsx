"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  RestaurantGrid,
  CategoryFilter,
  SortDropdown,
  SearchBar,
  type SortOption,
} from "@/components/restaurants";
import { useRestaurants } from "@/lib/hooks/use-restaurants";
import type { Restaurant } from "@/types/restaurant";

interface RestaurantsContentProps {
  initialCategory?: string;
  initialSearch?: string;
  initialSort?: string;
}

export function RestaurantsContent({
  initialCategory,
  initialSearch,
  initialSort,
}: RestaurantsContentProps) {
  const locale = useLocale();
  const t = useTranslations("restaurants");
  const router = useRouter();
  const searchParams = useSearchParams();

  const [category, setCategory] = useState<string | null>(initialCategory || null);
  const [search, setSearch] = useState(initialSearch || "");
  const [sort, setSort] = useState<SortOption>((initialSort as SortOption) || "newest");

  // Use real API data
  const { data, isLoading, isFetching } = useRestaurants({
    category: category || undefined,
    search: search || undefined,
    sortBy: sort,
  });

  // Use API data
  const restaurants = data?.restaurants || [];

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (search) params.set("q", search);
    if (sort !== "newest") params.set("sort", sort);

    const queryString = params.toString();
    const newUrl = queryString
      ? `/${locale}/restaurants?${queryString}`
      : `/${locale}/restaurants`;

    router.replace(newUrl, { scroll: false });
  }, [category, search, sort, locale, router]);

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="mb-2 text-3xl font-bold md:text-4xl">
            🍽️ {t("title")}
          </h1>
          <p className="text-muted-foreground">{t("subtitle")}</p>
        </motion.div>

        {/* Search Bar */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <SearchBar
            value={search}
            onChange={setSearch}
          />
        </motion.div>

        {/* Category Filter */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-6"
        >
          <CategoryFilter
            selectedCategory={category}
            onCategoryChange={setCategory}
          />
        </motion.div>

        {/* Results Count & Sort */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mb-6 flex items-center justify-between"
        >
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground">
              {restaurants.length} {locale === "ar" ? "مطعم" : "restaurants"}
            </span>
            {isFetching && (
              <Loader2 className="h-4 w-4 animate-spin text-primary-500" />
            )}
          </div>
          <SortDropdown value={sort} onChange={setSort} />
        </motion.div>

        {/* Restaurant Grid */}
        <RestaurantGrid
          restaurants={restaurants}
          isLoading={isLoading}
        />

        {/* Empty State */}
        {!isLoading && restaurants.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="py-20 text-center"
          >
            <div className="mb-4 text-6xl">🔍</div>
            <h3 className="mb-2 text-xl font-semibold">
              {locale === "ar" ? "لا توجد نتائج" : "No results found"}
            </h3>
            <p className="mb-6 text-muted-foreground">
              {locale === "ar"
                ? "جرب البحث بكلمات مختلفة أو تصفية أخرى"
                : "Try different search terms or filters"}
            </p>
            <Button
              variant="outline"
              onClick={() => {
                setCategory(null);
                setSearch("");
              }}
            >
              {locale === "ar" ? "مسح الفلاتر" : "Clear filters"}
            </Button>
          </motion.div>
        )}

        {/* Load More Button (for future pagination) */}
        {restaurants.length > 0 && restaurants.length >= 12 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="mt-8 text-center"
          >
            <Button variant="outline" size="lg">
              {t("loadMore")}
            </Button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
