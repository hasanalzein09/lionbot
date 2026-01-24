"use client";

import Link from "next/link";
import Image from "next/image";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { Star, Clock, MapPin } from "lucide-react";
import type { Restaurant } from "@/types/restaurant";

interface RestaurantCardProps {
  restaurant: Restaurant;
  index?: number;
}

export function RestaurantCard({ restaurant, index = 0 }: RestaurantCardProps) {
  const locale = useLocale();
  const t = useTranslations("restaurants");
  const isRTL = locale === "ar";

  // Handle both camelCase and snake_case from API
  const nameAr = restaurant.nameAr || restaurant.name_ar;
  const categoryAr = restaurant.categoryAr || restaurant.category_ar;
  const isOpen = restaurant.isOpen ?? restaurant.is_open;
  const isFeatured = restaurant.isFeatured ?? restaurant.is_featured;
  const deliveryTime = restaurant.deliveryTime || restaurant.delivery_time;

  const displayName = locale === "ar" && nameAr ? nameAr : restaurant.name;
  const displayCategory = locale === "ar" && categoryAr ? categoryAr : restaurant.category;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.4 }}
    >
      <Link href={`/${locale}/restaurants/${restaurant.slug}`}>
        <div className="group overflow-hidden rounded-2xl bg-white shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border border-gray-100">
          {/* Image Container */}
          <div className="relative aspect-[16/10] overflow-hidden">
            <Image
              src={restaurant.image || "/images/placeholder-restaurant.webp"}
              alt={displayName}
              fill
              className="object-cover transition-transform duration-500 group-hover:scale-105"
            />

            {/* Status Badge */}
            <div className={`absolute top-3 ${isRTL ? "right-3" : "left-3"}`}>
              {isOpen ? (
                <div className="flex items-center gap-1.5 rounded-full bg-emerald-500 px-3 py-1.5 text-xs font-medium text-white shadow-md">
                  <span className="relative flex h-2 w-2">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-white opacity-75"></span>
                    <span className="relative inline-flex h-2 w-2 rounded-full bg-white"></span>
                  </span>
                  {t("openNow")}
                </div>
              ) : (
                <div className="flex items-center gap-1.5 rounded-full bg-gray-500 px-3 py-1.5 text-xs font-medium text-white shadow-md">
                  <span className="h-2 w-2 rounded-full bg-white/60"></span>
                  {t("closed")}
                </div>
              )}
            </div>

            {/* Featured Badge */}
            {isFeatured && (
              <div className={`absolute top-3 ${isRTL ? "left-3" : "right-3"}`}>
                <div className="rounded-full bg-amber-400 px-2.5 py-1 text-xs font-semibold text-amber-900 shadow-md">
                  Featured
                </div>
              </div>
            )}

            {/* Category Tag */}
            {displayCategory && (
              <div className={`absolute bottom-3 ${isRTL ? "right-3" : "left-3"}`}>
                <span className="rounded-full bg-white/95 backdrop-blur-sm px-3 py-1.5 text-xs font-medium text-gray-700 shadow-sm">
                  {displayCategory}
                </span>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="p-4">
            {/* Title and Rating Row */}
            <div className="mb-3 flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 group-hover:text-emerald-600 transition-colors truncate text-lg">
                  {displayName}
                </h3>
                {restaurant.priceRange && (
                  <span className="text-sm text-emerald-600 font-medium">{restaurant.priceRange}</span>
                )}
              </div>

              {/* Rating with Gold Star */}
              {restaurant.rating && (
                <div className="flex items-center gap-1 rounded-lg bg-amber-50 px-2.5 py-1 flex-shrink-0 border border-amber-100">
                  <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                  <span className="text-sm font-semibold text-amber-700">
                    {restaurant.rating.toFixed(1)}
                  </span>
                </div>
              )}
            </div>

            {/* Meta Info */}
            <div className="flex items-center gap-4 text-sm text-gray-500">
              {deliveryTime && (
                <span className="flex items-center gap-1.5">
                  <Clock className="h-4 w-4 text-emerald-500" />
                  <span>
                    {deliveryTime.min}-{deliveryTime.max} {locale === "ar" ? "دقيقة" : "min"}
                  </span>
                </span>
              )}
              {restaurant.reviewCount && (
                <span className="text-gray-400">
                  ({restaurant.reviewCount} {locale === "ar" ? "تقييم" : "reviews"})
                </span>
              )}
            </div>

            {/* Delivery Fee */}
            {(restaurant.deliveryFee !== undefined || restaurant.delivery_fee !== undefined) && (
              <div className="mt-2 pt-2 border-t border-gray-100">
                <span className="text-xs text-gray-500">
                  {locale === "ar" ? "رسوم التوصيل: " : "Delivery: "}
                  <span className="font-medium text-emerald-600">
                    {(restaurant.deliveryFee ?? restaurant.delivery_fee) === 0
                      ? locale === "ar" ? "مجاني" : "Free"
                      : `$${restaurant.deliveryFee ?? restaurant.delivery_fee}`}
                  </span>
                </span>
              </div>
            )}
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
