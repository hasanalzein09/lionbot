"use client";

import { useLocale } from "next-intl";
import { motion } from "framer-motion";
import { MenuItemCard } from "./menu-item";
import { cn } from "@/lib/utils/cn";
import type { MenuCategory as MenuCategoryType, MenuItem } from "@/types/menu";

interface MenuCategoryProps {
  category: MenuCategoryType;
  onSelectItem: (item: MenuItem) => void;
}

export function MenuCategory({ category, onSelectItem }: MenuCategoryProps) {
  const locale = useLocale();
  const isRTL = locale === "ar";

  const nameAr = category.nameAr || category.name_ar;
  const displayName = locale === "ar" && nameAr ? nameAr : category.name;
  const items = category.items || [];

  if (items.length === 0) {
    return null;
  }

  return (
    <motion.section
      id={`category-${category.id}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="scroll-mt-32"
    >
      {/* Category Header */}
      <div className={cn(
        "mb-6 flex items-center gap-3",
        "pb-3 border-b border-gray-100"
      )}>
        <h2 className="text-xl font-bold text-gray-900">{displayName}</h2>
        <span className={cn(
          "rounded-full px-3 py-1 text-sm font-medium",
          "bg-emerald-50 text-emerald-600"
        )}>
          {items.length} {isRTL ? "صنف" : items.length === 1 ? "item" : "items"}
        </span>
      </div>

      {/* Divider Line */}
      <div className="mb-4 h-px w-full bg-gradient-to-r from-transparent via-gray-200 to-transparent" />

      {/* Items Grid */}
      <div className="grid gap-4 sm:grid-cols-2">
        {items.map((item, index) => (
          <MenuItemCard
            key={item.id}
            item={item}
            onSelect={onSelectItem}
            index={index}
          />
        ))}
      </div>
    </motion.section>
  );
}
