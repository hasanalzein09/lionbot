"use client";

import Link from "next/link";
import Image from "next/image";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { Star, Clock, ChevronLeft, ChevronRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useFeaturedRestaurants } from "@/lib/hooks/use-restaurants";
import type { Restaurant } from "@/types/restaurant";

export function FeaturedRestaurants() {
  const t = useTranslations("home.featured");
  const tCommon = useTranslations("common");
  const tRestaurants = useTranslations("restaurants");
  const locale = useLocale();

  // Fetch real data from API
  const { data: restaurants, isLoading } = useFeaturedRestaurants(6);

  return (
    <section className="py-12 md:py-16">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <motion.h2
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="text-2xl font-bold md:text-3xl"
          >
            ⭐ {t("title")}
          </motion.h2>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <Link href={`/${locale}/restaurants`}>
              <Button variant="ghost" className="group">
                {tCommon("viewAll")}
                {locale === "ar" ? (
                  <ChevronLeft className="ms-1 h-4 w-4 transition-transform group-hover:-translate-x-1" />
                ) : (
                  <ChevronRight className="ms-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
                )}
              </Button>
            </Link>
          </motion.div>
        </div>

        {/* Grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {isLoading ? (
            // Loading skeletons
            Array.from({ length: 4 }).map((_, index) => (
              <RestaurantCardSkeleton key={index} />
            ))
          ) : restaurants && restaurants.length > 0 ? (
            restaurants.map((restaurant, index) => (
              <RestaurantCard
                key={restaurant.id}
                restaurant={restaurant}
                locale={locale}
                index={index}
                tRestaurants={tRestaurants}
              />
            ))
          ) : (
            <p className="col-span-full text-center text-muted-foreground py-8">
              {locale === "ar" ? "لا توجد مطاعم متاحة" : "No restaurants available"}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

interface RestaurantCardProps {
  restaurant: Restaurant;
  locale: string;
  index: number;
  tRestaurants: ReturnType<typeof useTranslations>;
}

function RestaurantCard({ restaurant, locale, index, tRestaurants }: RestaurantCardProps) {
  // Handle both camelCase and snake_case from API
  const nameAr = restaurant.nameAr || restaurant.name_ar;
  const categoryAr = restaurant.categoryAr || restaurant.category_ar;
  const slug = restaurant.slug || restaurant.name.toLowerCase().replace(/\s+/g, "-").replace(/&/g, "and");

  const displayName = locale === "ar" && nameAr ? nameAr : restaurant.name;
  const displayCategory = locale === "ar" && categoryAr ? categoryAr : restaurant.category;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.1 }}
    >
      <Link href={`/${locale}/restaurants/${slug}`}>
        <div className="group overflow-hidden rounded-2xl bg-secondary-800 transition-all hover:shadow-xl hover:shadow-primary-500/10">
          {/* Image */}
          <div className="relative aspect-[4/3] overflow-hidden">
            {restaurant.image ? (
              <Image
                src={restaurant.image}
                alt={displayName}
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
                className="object-cover transition-transform duration-300 group-hover:scale-110"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center bg-secondary-700 text-6xl">
                🍽️
              </div>
            )}

            {/* Featured Badge */}
            <div className="absolute right-3 top-3">
              <Badge variant="warning">⭐</Badge>
            </div>

            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
          </div>

          {/* Content */}
          <div className="p-4">
            <div className="mb-2 flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-foreground group-hover:text-primary-500 transition-colors line-clamp-1">
                  {displayName}
                </h3>
                <p className="text-sm text-muted-foreground line-clamp-1">{displayCategory}</p>
              </div>
            </div>

            {/* Phone */}
            {restaurant.phone && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>📞</span>
                <span className="truncate">{restaurant.phone}</span>
              </div>
            )}
          </div>
        </div>
      </Link>
    </motion.div>
  );
}

function RestaurantCardSkeleton() {
  return (
    <div className="overflow-hidden rounded-2xl bg-secondary-800">
      <Skeleton className="aspect-[4/3] w-full" />
      <div className="p-4 space-y-2">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
      </div>
    </div>
  );
}
