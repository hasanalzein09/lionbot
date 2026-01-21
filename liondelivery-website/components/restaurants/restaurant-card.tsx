"use client";

import Link from "next/link";
import Image from "next/image";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { Star, Clock, MapPin } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { Restaurant } from "@/types/restaurant";

interface RestaurantCardProps {
  restaurant: Restaurant;
  index?: number;
}

export function RestaurantCard({ restaurant, index = 0 }: RestaurantCardProps) {
  const locale = useLocale();
  const t = useTranslations("restaurants");

  const displayName = locale === "ar" && restaurant.nameAr ? restaurant.nameAr : restaurant.name;
  const displayCategory = locale === "ar" && restaurant.categoryAr ? restaurant.categoryAr : restaurant.category;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Link href={`/${locale}/restaurants/${restaurant.slug}`}>
        <div className="group overflow-hidden rounded-2xl bg-secondary-800 transition-all duration-300 hover:shadow-xl hover:shadow-primary-500/10 hover:-translate-y-1">
          {/* Image */}
          <div className="relative aspect-[16/10] overflow-hidden">
            <Image
              src={restaurant.image || "/images/placeholder-restaurant.webp"}
              alt={displayName}
              fill
              className="object-cover transition-transform duration-500 group-hover:scale-110"
            />

            {/* Status Badge */}
            <div className="absolute left-3 top-3">
              <Badge variant={restaurant.isOpen ? "success" : "secondary"}>
                {restaurant.isOpen ? t("openNow") : t("closed")}
              </Badge>
            </div>

            {/* Featured Badge */}
            {restaurant.isFeatured && (
              <div className="absolute right-3 top-3">
                <Badge variant="warning">🔥</Badge>
              </div>
            )}

            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />

            {/* Category on Image */}
            <div className="absolute bottom-3 left-3">
              <span className="rounded-full bg-white/20 px-3 py-1 text-xs font-medium text-white backdrop-blur-sm">
                {displayCategory}
              </span>
            </div>
          </div>

          {/* Content */}
          <div className="p-4">
            <div className="mb-3 flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-foreground group-hover:text-primary-500 transition-colors truncate text-lg">
                  {displayName}
                </h3>
                {restaurant.priceRange && (
                  <span className="text-sm text-primary-500">{restaurant.priceRange}</span>
                )}
              </div>

              {/* Rating */}
              {restaurant.rating && (
                <div className="flex items-center gap-1 rounded-lg bg-primary-500/10 px-2 py-1 flex-shrink-0">
                  <Star className="h-3.5 w-3.5 fill-primary-500 text-primary-500" />
                  <span className="text-sm font-medium text-primary-500">
                    {restaurant.rating}
                  </span>
                </div>
              )}
            </div>

            {/* Meta Info */}
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              {restaurant.deliveryTime && (
                <span className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  {restaurant.deliveryTime.min}-{restaurant.deliveryTime.max}{" "}
                  {locale === "ar" ? "دقيقة" : "min"}
                </span>
              )}
              {restaurant.reviewCount && (
                <span className="text-muted-foreground">
                  ({restaurant.reviewCount} {locale === "ar" ? "تقييم" : "reviews"})
                </span>
              )}
            </div>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
