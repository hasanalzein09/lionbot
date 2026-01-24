"use client";

import Link from "next/link";
import Image from "next/image";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { Star, Clock, ChevronLeft, ChevronRight, MapPin } from "lucide-react";
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
    <section className="bg-gradient-to-b from-white to-gray-50 py-12 md:py-20">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-10 flex items-end justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <span className="mb-2 inline-block rounded-full bg-amber-100 px-3 py-1 text-sm font-medium text-amber-700">
              {locale === "ar" ? "الافضل تقييما" : "Top Rated"}
            </span>
            <h2 className="text-2xl font-bold text-gray-900 md:text-3xl lg:text-4xl">
              {t("title")}
            </h2>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <Link
              href={`/${locale}/restaurants`}
              className="group flex items-center gap-1 text-sm font-semibold text-emerald-600 transition-colors hover:text-emerald-700"
            >
              {tCommon("viewAll")}
              {locale === "ar" ? (
                <ChevronLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
              ) : (
                <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              )}
            </Link>
          </motion.div>
        </div>

        {/* Grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
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
            <p className="col-span-full py-12 text-center text-gray-500">
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

  // Generate random rating for display (in real app, this would come from API)
  const rating = ((restaurant.id % 10) / 10 + 4).toFixed(1);
  const isOpen = true; // In real app, check operating hours

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.1 }}
    >
      <Link href={`/${locale}/restaurants/${slug}`}>
        <div className="group overflow-hidden rounded-2xl bg-white shadow-md ring-1 ring-gray-100 transition-all duration-300 hover:-translate-y-2 hover:shadow-xl hover:shadow-emerald-500/10">
          {/* Image */}
          <div className="relative aspect-[4/3] overflow-hidden bg-gray-100">
            {restaurant.image ? (
              <Image
                src={restaurant.image}
                alt={displayName}
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
                className="object-cover transition-transform duration-500 group-hover:scale-110"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-emerald-50 to-teal-50 text-6xl">
                🍽️
              </div>
            )}

            {/* Open Badge */}
            {isOpen && (
              <div className="absolute start-3 top-3">
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500 px-2.5 py-1 text-xs font-semibold text-white shadow-lg shadow-emerald-500/30">
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-white" />
                  {locale === "ar" ? "مفتوح" : "Open"}
                </span>
              </div>
            )}

            {/* Rating Badge */}
            <div className="absolute end-3 top-3">
              <span className="inline-flex items-center gap-1 rounded-full bg-white/90 px-2.5 py-1 text-sm font-bold text-gray-900 shadow-lg backdrop-blur-sm">
                <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
                {rating}
              </span>
            </div>
          </div>

          {/* Content */}
          <div className="p-4">
            <div className="mb-3">
              <h3 className="font-bold text-gray-900 transition-colors group-hover:text-emerald-600 line-clamp-1">
                {displayName}
              </h3>
              <p className="text-sm text-gray-500 line-clamp-1">{displayCategory}</p>
            </div>

            {/* Info Row */}
            <div className="flex items-center justify-between text-sm">
              {/* Delivery Time */}
              <div className="flex items-center gap-1 text-gray-500">
                <Clock className="h-4 w-4" />
                <span>25-35 {locale === "ar" ? "دقيقة" : "min"}</span>
              </div>

              {/* Phone */}
              {restaurant.phone && (
                <div className="flex items-center gap-1 text-gray-400">
                  <MapPin className="h-4 w-4" />
                  <span className="text-xs truncate max-w-[80px]">{restaurant.phone}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}

function RestaurantCardSkeleton() {
  return (
    <div className="overflow-hidden rounded-2xl bg-white shadow-md ring-1 ring-gray-100">
      <Skeleton className="aspect-[4/3] w-full" />
      <div className="space-y-3 p-4">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
        <div className="flex items-center justify-between">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-16" />
        </div>
      </div>
    </div>
  );
}
