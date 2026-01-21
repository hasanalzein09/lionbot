"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import {
  Star,
  Clock,
  Phone,
  MapPin,
  Share2,
  ChevronLeft,
  ChevronRight,
  ShoppingCart,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { MenuSection } from "@/components/menu/menu-section";
import { useCartStore } from "@/lib/stores/cart-store";
import { formatPrice } from "@/lib/utils/formatters";
import type { Restaurant } from "@/types/restaurant";
import type { Menu, MenuCategory, MenuItem } from "@/types/menu";

// Mock data for development
const mockRestaurant: Restaurant = {
  id: "1",
  name: "Burgero",
  nameAr: "برغيرو",
  slug: "burgero",
  description: "The best burgers in Saida. Fresh ingredients, amazing taste.",
  descriptionAr: "أفضل برغر في صيدا. مكونات طازجة، طعم مذهل.",
  image: "/images/placeholder-restaurant.webp",
  coverImage: "/images/placeholder-restaurant.webp",
  category: "Burger",
  categoryAr: "برغر",
  rating: 4.8,
  reviewCount: 120,
  priceRange: "$$",
  deliveryTime: { min: 25, max: 35 },
  deliveryFee: 2,
  isOpen: true,
  phone: "+96170000000",
  address: "Saida, Lebanon",
};

const mockMenu: Menu = {
  restaurantId: "1",
  categories: [
    {
      id: "burgers",
      name: "Burgers",
      nameAr: "برغر",
      items: [
        {
          id: "1",
          name: "Classic Burger",
          nameAr: "كلاسيك برغر",
          description: "100% beef patty with fresh lettuce, tomato, and special sauce",
          descriptionAr: "لحم بقري 100% مع خس طازج وطماطم وصوص خاص",
          price: 5.0,
          image: "/images/placeholder-food.webp",
          categoryId: "burgers",
          restaurantId: "1",
          isPopular: true,
          variants: [
            { id: "single", name: "Single", nameAr: "سينجل", price: 5.0, isDefault: true },
            { id: "double", name: "Double", nameAr: "دبل", price: 7.0 },
            { id: "triple", name: "Triple", nameAr: "تربل", price: 9.0 },
          ],
          addons: [
            { id: "cheese", name: "Extra Cheese", nameAr: "جبنة إضافية", price: 1.0 },
            { id: "egg", name: "Fried Egg", nameAr: "بيض مقلي", price: 0.5 },
            { id: "bacon", name: "Bacon", nameAr: "بيكون", price: 1.5 },
          ],
        },
        {
          id: "2",
          name: "Cheese Burger",
          nameAr: "تشيز برغر",
          description: "Double cheddar cheese with beef patty",
          descriptionAr: "جبنة شيدر مزدوجة مع لحم بقري",
          price: 6.0,
          image: "/images/placeholder-food.webp",
          categoryId: "burgers",
          restaurantId: "1",
        },
        {
          id: "3",
          name: "Mushroom Burger",
          nameAr: "ماشروم برغر",
          description: "Fresh mushrooms with special mushroom sauce",
          descriptionAr: "فطر طازج مع صوص فطر خاص",
          price: 7.0,
          image: "/images/placeholder-food.webp",
          categoryId: "burgers",
          restaurantId: "1",
        },
      ],
    },
    {
      id: "sides",
      name: "Sides",
      nameAr: "جانبية",
      items: [
        {
          id: "4",
          name: "French Fries",
          nameAr: "بطاطا مقلية",
          description: "Crispy golden fries",
          descriptionAr: "بطاطا مقرمشة ذهبية",
          price: 2.5,
          image: "/images/placeholder-food.webp",
          categoryId: "sides",
          restaurantId: "1",
        },
        {
          id: "5",
          name: "Onion Rings",
          nameAr: "حلقات البصل",
          description: "Crispy onion rings",
          descriptionAr: "حلقات بصل مقرمشة",
          price: 3.0,
          image: "/images/placeholder-food.webp",
          categoryId: "sides",
          restaurantId: "1",
        },
      ],
    },
    {
      id: "drinks",
      name: "Drinks",
      nameAr: "مشروبات",
      items: [
        {
          id: "6",
          name: "Coca Cola",
          nameAr: "كوكا كولا",
          price: 1.5,
          categoryId: "drinks",
          restaurantId: "1",
        },
        {
          id: "7",
          name: "Fresh Orange Juice",
          nameAr: "عصير برتقال طازج",
          price: 3.0,
          categoryId: "drinks",
          restaurantId: "1",
        },
      ],
    },
  ],
};

interface RestaurantDetailContentProps {
  slug: string;
}

export function RestaurantDetailContent({ slug }: RestaurantDetailContentProps) {
  const locale = useLocale();
  const t = useTranslations("restaurant");
  const tCommon = useTranslations("common");

  // In production, use useRestaurant hook
  // const { data: restaurant, isLoading } = useRestaurant(slug);
  const restaurant = mockRestaurant;
  const menu = mockMenu;

  const { items: cartItems, getSubtotal, getTotalItems } = useCartStore();

  const displayName = locale === "ar" && restaurant.nameAr ? restaurant.nameAr : restaurant.name;
  const displayDescription =
    locale === "ar" && restaurant.descriptionAr
      ? restaurant.descriptionAr
      : restaurant.description;
  const displayCategory =
    locale === "ar" && restaurant.categoryAr ? restaurant.categoryAr : restaurant.category;

  const cartItemsCount = getTotalItems();
  const cartTotal = getSubtotal();

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: displayName,
          text: displayDescription,
          url: window.location.href,
        });
      } catch (err) {
        // User cancelled or error
      }
    } else {
      // Fallback - copy to clipboard
      navigator.clipboard.writeText(window.location.href);
    }
  };

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Hero Section */}
      <div className="relative">
        {/* Cover Image */}
        <div className="relative h-48 w-full md:h-64">
          <Image
            src={restaurant.coverImage || restaurant.image || "/images/placeholder-restaurant.webp"}
            alt={displayName}
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-t from-background via-background/50 to-transparent" />
        </div>

        {/* Restaurant Info */}
        <div className="container mx-auto px-4">
          <div className="relative -mt-20">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl bg-secondary-800 p-6 shadow-xl"
            >
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                {/* Info */}
                <div className="flex-1">
                  <div className="mb-2 flex items-center gap-2">
                    <Badge variant={restaurant.isOpen ? "success" : "secondary"}>
                      {restaurant.isOpen
                        ? locale === "ar"
                          ? "مفتوح الآن"
                          : "Open Now"
                        : locale === "ar"
                        ? "مغلق"
                        : "Closed"}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      {displayCategory}
                    </span>
                  </div>

                  <h1 className="mb-2 text-2xl font-bold md:text-3xl">{displayName}</h1>

                  {displayDescription && (
                    <p className="mb-4 text-muted-foreground">{displayDescription}</p>
                  )}

                  {/* Meta */}
                  <div className="flex flex-wrap items-center gap-4 text-sm">
                    {restaurant.rating && (
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4 fill-primary-500 text-primary-500" />
                        <span className="font-medium">{restaurant.rating}</span>
                        <span className="text-muted-foreground">
                          ({restaurant.reviewCount})
                        </span>
                      </div>
                    )}
                    {restaurant.deliveryTime && (
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        <span>
                          {restaurant.deliveryTime.min}-{restaurant.deliveryTime.max}{" "}
                          {locale === "ar" ? "دقيقة" : "min"}
                        </span>
                      </div>
                    )}
                    {restaurant.priceRange && (
                      <span className="text-primary-500">{restaurant.priceRange}</span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {restaurant.phone && (
                    <a href={`tel:${restaurant.phone}`}>
                      <Button variant="outline" size="icon">
                        <Phone className="h-4 w-4" />
                      </Button>
                    </a>
                  )}
                  <Button variant="outline" size="icon" onClick={handleShare}>
                    <Share2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Menu Section */}
      <div className="container mx-auto px-4 py-8">
        {/* Breadcrumbs */}
        <div className="mb-6">
          <Breadcrumbs
            items={[
              { label: locale === "ar" ? "المطاعم" : "Restaurants", href: `/${locale}/restaurants` },
              { label: displayName },
            ]}
          />
        </div>

        {/* Menu */}
        <MenuSection
          menu={menu}
          restaurantId={restaurant.id}
          restaurantName={restaurant.name}
          restaurantNameAr={restaurant.nameAr}
        />
      </div>

      {/* Sticky Cart Bar */}
      {cartItemsCount > 0 && (
        <motion.div
          initial={{ y: 100 }}
          animate={{ y: 0 }}
          className="fixed bottom-0 inset-x-0 z-40 border-t border-border bg-secondary-900/95 backdrop-blur-lg"
        >
          <div className="container mx-auto px-4 py-4">
            <Link href={`/${locale}/cart`}>
              <Button className="w-full" size="lg">
                <ShoppingCart className="mr-2 h-5 w-5" />
                <span>
                  {cartItemsCount} {locale === "ar" ? "صنف" : "items"}
                </span>
                <span className="mx-2">•</span>
                <span>{formatPrice(cartTotal)}</span>
                {locale === "ar" ? (
                  <ChevronLeft className="ml-2 h-5 w-5" />
                ) : (
                  <ChevronRight className="ml-2 h-5 w-5" />
                )}
              </Button>
            </Link>
          </div>
        </motion.div>
      )}
    </div>
  );
}
