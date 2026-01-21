"use client";

import { useLocale } from "next-intl";
import { motion } from "framer-motion";
import { MenuItemCard } from "./menu-item";
import type { MenuCategory as MenuCategoryType, MenuItem } from "@/types/menu";

interface MenuCategoryProps {
  category: MenuCategoryType;
  onSelectItem: (item: MenuItem) => void;
}

export function MenuCategory({ category, onSelectItem }: MenuCategoryProps) {
  const locale = useLocale();

  const displayName = locale === "ar" && category.nameAr ? category.nameAr : category.name;
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
      <div className="mb-4 flex items-center gap-3">
        <h2 className="text-xl font-bold">{displayName}</h2>
        <span className="rounded-full bg-secondary-800 px-3 py-1 text-sm text-muted-foreground">
          {items.length} {locale === "ar" ? "صنف" : "items"}
        </span>
      </div>

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
