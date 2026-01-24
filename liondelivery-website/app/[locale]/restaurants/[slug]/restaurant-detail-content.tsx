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
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { MenuSection } from "@/components/menu/menu-section";
import { useCartStore } from "@/lib/stores/cart-store";
import { formatPrice } from "@/lib/utils/formatters";
import { useRestaurant } from "@/lib/hooks/use-restaurants";
import { useMenu } from "@/lib/hooks/use-menu";
import type { Restaurant } from "@/types/restaurant";
import type { Menu, MenuCategory, MenuItem } from "@/types/menu";

interface RestaurantDetailContentProps {
  slug: string;
}

export function RestaurantDetailContent({ slug }: RestaurantDetailContentProps) {
  const locale = useLocale();
  const t = useTranslations("restaurant");
  const tCommon = useTranslations("common");

  // Fetch real data from API
  const { data: restaurant, isLoading: isLoadingRestaurant, error: restaurantError } = useRestaurant(slug);
  const { data: menu, isLoading: isLoadingMenu } = useMenu(restaurant?.id?.toString() || "");

  const { items: cartItems, getSubtotal, getTotalItems } = useCartStore();

  // Loading state
  if (isLoadingRestaurant) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
      </div>
    );
  }

  // Error state
  if (restaurantError || !restaurant) {
    return (
      <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4">
        <p className="text-lg text-muted-foreground">
          {locale === "ar" ? "لم يتم العثور على المطعم" : "Restaurant not found"}
        </p>
        <Link href={`/${locale}/restaurants`}>
          <Button>{locale === "ar" ? "عرض جميع المطاعم" : "View All Restaurants"}</Button>
        </Link>
      </div>
    );
  }

  // Handle both camelCase and snake_case from API
  const nameAr = restaurant.nameAr || restaurant.name_ar;
  const descriptionAr = restaurant.descriptionAr || restaurant.description_ar;
  const categoryAr = restaurant.categoryAr || restaurant.category_ar;

  const displayName = locale === "ar" && nameAr ? nameAr : restaurant.name;
  const displayDescription =
    locale === "ar" && descriptionAr
      ? descriptionAr
      : restaurant.description;
  const displayCategory =
    locale === "ar" && categoryAr ? categoryAr : restaurant.category;

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
                    <Badge variant={restaurant.isOpen !== false ? "success" : "secondary"}>
                      {restaurant.isOpen !== false
                        ? locale === "ar"
                          ? "مفتوح الآن"
                          : "Open Now"
                        : locale === "ar"
                        ? "مغلق"
                        : "Closed"}
                    </Badge>
                    {displayCategory && (
                      <span className="text-sm text-muted-foreground">
                        {displayCategory}
                      </span>
                    )}
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
        {isLoadingMenu ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
          </div>
        ) : menu && menu.categories && menu.categories.length > 0 ? (
          <MenuSection
            menu={menu}
            restaurantId={String(restaurant.id)}
            restaurantName={restaurant.name}
            restaurantNameAr={nameAr}
          />
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <p className="text-lg text-muted-foreground">
              {locale === "ar" ? "لا توجد قائمة متاحة" : "No menu available"}
            </p>
          </div>
        )}
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
