"use client";

import { useState, useEffect } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { MenuCategory } from "./menu-category";
import { MenuCategoryNav } from "./menu-category-nav";
import { MenuItemModal } from "./menu-item-modal";
import { useDebounce } from "@/lib/hooks/use-debounce";
import type { Menu, MenuCategory as MenuCategoryType, MenuItem } from "@/types/menu";

interface MenuSectionProps {
  menu: Menu;
  restaurantId: string;
  restaurantName: string;
  restaurantNameAr?: string;
}

export function MenuSection({
  menu,
  restaurantId,
  restaurantName,
  restaurantNameAr,
}: MenuSectionProps) {
  const locale = useLocale();
  const t = useTranslations("restaurant");

  const [activeCategory, setActiveCategory] = useState<string | number>(menu.categories[0]?.id || "");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const debouncedSearch = useDebounce(searchQuery, 300);

  // Filter categories and items based on search
  const filteredCategories = menu.categories
    .map((category) => {
      if (!debouncedSearch) return category;

      const filteredItems = category.items?.filter((item) => {
        const searchLower = debouncedSearch.toLowerCase();
        const nameAr = item.nameAr || item.name_ar;
        const descriptionAr = item.descriptionAr || item.description_ar;
        return (
          item.name.toLowerCase().includes(searchLower) ||
          nameAr?.includes(debouncedSearch) ||
          item.description?.toLowerCase().includes(searchLower) ||
          descriptionAr?.includes(debouncedSearch)
        );
      });

      return { ...category, items: filteredItems };
    })
    .filter((category) => (category.items?.length || 0) > 0);

  // Update active category based on scroll position
  useEffect(() => {
    if (debouncedSearch) return;

    const handleScroll = () => {
      const categories = menu.categories;
      const scrollPosition = window.scrollY + 200;

      for (let i = categories.length - 1; i >= 0; i--) {
        const element = document.getElementById(`category-${categories[i].id}`);
        if (element && element.offsetTop <= scrollPosition) {
          setActiveCategory(categories[i].id);
          break;
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [menu.categories, debouncedSearch]);

  const handleSelectItem = (item: MenuItem) => {
    setSelectedItem(item);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setSelectedItem(null), 300);
  };

  return (
    <div>
      {/* Search Bar */}
      <div className="relative mb-4">
        <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={t("searchMenu")}
          className="h-12 pl-12 pr-10 rounded-xl"
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-1 text-muted-foreground transition-colors hover:bg-secondary-700 hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Category Navigation */}
      {!debouncedSearch && (
        <MenuCategoryNav
          categories={menu.categories.map((c) => ({
            ...c,
            itemCount: c.items?.length || 0,
          }))}
          activeCategory={activeCategory}
          onCategoryClick={setActiveCategory}
        />
      )}

      {/* Menu Categories */}
      <div className="mt-6 space-y-8">
        {filteredCategories.map((category) => (
          <MenuCategory
            key={category.id}
            category={category}
            onSelectItem={handleSelectItem}
          />
        ))}

        {/* Empty State */}
        {filteredCategories.length === 0 && (
          <div className="py-20 text-center">
            <div className="mb-4 text-6xl">🔍</div>
            <h3 className="mb-2 text-xl font-semibold">
              {locale === "ar" ? "لا توجد نتائج" : "No results found"}
            </h3>
            <p className="text-muted-foreground">
              {locale === "ar"
                ? "جرب البحث بكلمات مختلفة"
                : "Try different search terms"}
            </p>
          </div>
        )}
      </div>

      {/* Menu Item Modal */}
      <MenuItemModal
        item={selectedItem}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        restaurantId={restaurantId}
        restaurantName={restaurantName}
        restaurantNameAr={restaurantNameAr}
      />
    </div>
  );
}
