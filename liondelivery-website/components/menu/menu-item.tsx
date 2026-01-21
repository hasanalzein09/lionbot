"use client";

import Image from "next/image";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { Plus, Flame } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatPrice } from "@/lib/utils/formatters";
import type { MenuItem } from "@/types/menu";

interface MenuItemCardProps {
  item: MenuItem;
  onSelect: (item: MenuItem) => void;
  index?: number;
}

export function MenuItemCard({ item, onSelect, index = 0 }: MenuItemCardProps) {
  const locale = useLocale();
  const t = useTranslations("menu");

  const displayName = locale === "ar" && item.nameAr ? item.nameAr : item.name;
  const displayDescription =
    locale === "ar" && item.descriptionAr ? item.descriptionAr : item.description;

  const hasDiscount = item.originalPrice && item.originalPrice > item.price;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="group"
    >
      <button
        onClick={() => onSelect(item)}
        className="flex w-full gap-4 rounded-2xl bg-secondary-800 p-4 text-start transition-all hover:bg-secondary-700 hover:shadow-lg"
      >
        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="mb-1 flex items-start gap-2">
            <h3 className="font-semibold text-foreground group-hover:text-primary-500 transition-colors line-clamp-1">
              {displayName}
            </h3>
            {item.isPopular && (
              <Badge variant="warning" className="flex-shrink-0">
                <Flame className="mr-1 h-3 w-3" />
                {locale === "ar" ? "مميز" : "Popular"}
              </Badge>
            )}
          </div>

          {displayDescription && (
            <p className="mb-3 text-sm text-muted-foreground line-clamp-2">
              {displayDescription}
            </p>
          )}

          {/* Price */}
          <div className="flex items-center gap-2">
            <span className="font-semibold text-primary-500">
              {formatPrice(item.price)}
            </span>
            {hasDiscount && (
              <span className="text-sm text-muted-foreground line-through">
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
                className="object-cover transition-transform group-hover:scale-110"
              />
            </div>
          ) : (
            <div className="flex h-24 w-24 items-center justify-center rounded-xl bg-secondary-700 text-4xl">
              🍽️
            </div>
          )}

          {/* Add Button */}
          <div className="absolute -bottom-2 -right-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-500 text-white shadow-lg transition-transform group-hover:scale-110">
              <Plus className="h-5 w-5" />
            </div>
          </div>
        </div>
      </button>
    </motion.div>
  );
}
