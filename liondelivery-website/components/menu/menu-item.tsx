"use client";

import Image from "next/image";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { Plus, Flame } from "lucide-react";
import { formatPrice } from "@/lib/utils/formatters";
import { cn } from "@/lib/utils/cn";
import type { MenuItem } from "@/types/menu";

interface MenuItemCardProps {
  item: MenuItem;
  onSelect: (item: MenuItem) => void;
  index?: number;
}

export function MenuItemCard({ item, onSelect, index = 0 }: MenuItemCardProps) {
  const locale = useLocale();
  const t = useTranslations("menu");
  const isRTL = locale === "ar";

  // Handle both camelCase and snake_case from API
  const nameAr = item.nameAr || item.name_ar;
  const descriptionAr = item.descriptionAr || item.description_ar;
  const price = item.price ?? item.price_min ?? 0;
  const isPopular = item.isPopular || item.is_popular;
  const hasVariants = item.hasVariants || item.has_variants;
  const isAvailable = item.isAvailable ?? item.is_available ?? true;

  const displayName = locale === "ar" && nameAr ? nameAr : item.name;
  const displayDescription =
    locale === "ar" && descriptionAr ? descriptionAr : item.description;

  const hasDiscount = item.originalPrice && item.originalPrice > price;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="group"
    >
      <button
        onClick={() => isAvailable && onSelect(item)}
        disabled={!isAvailable}
        className={cn(
          "relative flex w-full gap-4 rounded-2xl bg-white p-4 text-start transition-all duration-300",
          "shadow-sm hover:shadow-lg hover:shadow-emerald-500/10",
          "border border-gray-100",
          isAvailable
            ? "hover:-translate-y-1 cursor-pointer"
            : "cursor-not-allowed"
        )}
      >
        {/* Sold Out Overlay */}
        {!isAvailable && (
          <div className="absolute inset-0 z-10 flex items-center justify-center rounded-2xl bg-white/80 backdrop-blur-sm">
            <span className="rounded-full bg-gray-900 px-4 py-2 text-sm font-semibold text-white">
              {isRTL ? "نفذت الكمية" : "Sold Out"}
            </span>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="mb-1 flex items-start gap-2 flex-wrap">
            <h3 className={cn(
              "font-semibold text-gray-900 transition-colors line-clamp-1",
              isAvailable && "group-hover:text-emerald-600"
            )}>
              {displayName}
            </h3>
            {isAvailable && isPopular && (
              <span className={cn(
                "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
                "bg-[#f43f5e]/10 text-[#f43f5e]"
              )}>
                <Flame className="h-3 w-3" />
                {isRTL ? "مميز" : "Popular"}
              </span>
            )}
          </div>

          {displayDescription && (
            <p className="mb-3 text-sm text-gray-500 line-clamp-2">
              {displayDescription}
            </p>
          )}

          {/* Price */}
          <div className="flex items-center gap-2">
            <span className="font-bold text-emerald-600">
              {hasVariants && item.price_min && item.price_max && item.price_min !== item.price_max
                ? `${formatPrice(item.price_min)} - ${formatPrice(item.price_max)}`
                : formatPrice(price)}
            </span>
            {hasDiscount && (
              <span className="text-sm text-gray-400 line-through">
                {formatPrice(item.originalPrice!)}
              </span>
            )}
          </div>
        </div>

        {/* Image & Add Button */}
        <div className="relative flex-shrink-0">
          {item.image ? (
            <div className="relative h-24 w-24 overflow-hidden rounded-xl">
              <Image
                src={item.image}
                alt={displayName}
                fill
                className={cn(
                  "object-cover transition-transform duration-300",
                  isAvailable && "group-hover:scale-110"
                )}
              />
            </div>
          ) : (
            <div className="flex h-24 w-24 items-center justify-center rounded-xl bg-gray-100 text-4xl">
              <span role="img" aria-label="food">&#127869;</span>
            </div>
          )}

          {/* Add Button */}
          {isAvailable && (
            <div className={cn(
              "absolute -bottom-2",
              isRTL ? "-left-2" : "-right-2"
            )}>
              <div className={cn(
                "flex h-9 w-9 items-center justify-center rounded-full",
                "bg-emerald-500 text-white shadow-lg shadow-emerald-500/30",
                "transition-all duration-300",
                "group-hover:scale-110 group-hover:bg-emerald-600"
              )}>
                <Plus className="h-5 w-5" />
              </div>
            </div>
          )}
        </div>
      </button>
    </motion.div>
  );
}
