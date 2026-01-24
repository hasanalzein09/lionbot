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
  Heart,
  ArrowLeft,
  ArrowRight,
  Info,
  Bike,
  DollarSign,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MenuSection } from "@/components/menu/menu-section";
import { useCartStore } from "@/lib/stores/cart-store";
import { formatPrice } from "@/lib/utils/formatters";
import { useRestaurant } from "@/lib/hooks/use-restaurants";
import { useMenu } from "@/lib/hooks/use-menu";
import { cn } from "@/lib/utils/cn";
import type { Restaurant } from "@/types/restaurant";
import type { Menu, MenuCategory, MenuItem } from "@/types/menu";

interface RestaurantDetailContentProps {
  slug: string;
}

export function RestaurantDetailContent({ slug }: RestaurantDetailContentProps) {
  const locale = useLocale();
  const isRTL = locale === "ar";
  const t = useTranslations("restaurant");
  const tCommon = useTranslations("common");

  const [isFavorite, setIsFavorite] = useState(false);

  // Fetch real data from API
  const { data: restaurant, isLoading: isLoadingRestaurant, error: restaurantError } = useRestaurant(slug);
  const { data: menu, isLoading: isLoadingMenu } = useMenu(restaurant?.id?.toString() || "");

  const { items: cartItems, getSubtotal, getTotalItems } = useCartStore();

  // Loading state
  if (isLoadingRestaurant) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center bg-white">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  // Error state
  if (restaurantError || !restaurant) {
    return (
      <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 bg-white">
        <p className="text-lg text-gray-500">
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

  const handleToggleFavorite = () => {
    setIsFavorite(!isFavorite);
    // In real app, save to favorites API
  };

  // Format working hours for display
  const getWorkingHoursDisplay = () => {
    // This would be more sophisticated in a real app
    return locale === "ar" ? "9:00 ص - 11:00 م" : "9:00 AM - 11:00 PM";
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-28">
      {/* Fixed Header */}
      <div className="fixed inset-x-0 top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="container mx-auto px-4">
          <div className="flex h-14 items-center justify-between">
            {/* Back Button */}
            <Link href={`/${locale}/restaurants`}>
              <Button
                variant="ghost"
                size="icon"
                className="h-10 w-10 rounded-full text-gray-700 hover:bg-gray-100"
              >
                {isRTL ? (
                  <ArrowRight className="h-5 w-5" />
                ) : (
                  <ArrowLeft className="h-5 w-5" />
                )}
              </Button>
            </Link>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleToggleFavorite}
                className={cn(
                  "h-10 w-10 rounded-full",
                  isFavorite ? "text-red-500 hover:bg-red-50" : "text-gray-700 hover:bg-gray-100"
                )}
              >
                <Heart className={cn("h-5 w-5", isFavorite && "fill-current")} />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleShare}
                className="h-10 w-10 rounded-full text-gray-700 hover:bg-gray-100"
              >
                <Share2 className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section with Image */}
      <div className="relative pt-14">
        <div className="relative h-56 w-full md:h-72 lg:h-80">
          <Image
            src={restaurant.coverImage || restaurant.image || "/images/placeholder-restaurant.webp"}
            alt={displayName}
            fill
            className="object-cover"
            priority
          />
          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
        </div>

        {/* White Info Card - Overlapping */}
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            className="relative -mt-24 rounded-3xl bg-white p-6 shadow-xl shadow-gray-200/50 ring-1 ring-gray-100"
          >
            {/* Status Badge */}
            <div className="mb-4 flex flex-wrap items-center gap-2">
              <Badge
                variant={restaurant.isOpen !== false ? "success" : "secondary"}
                dot
                className={cn(
                  restaurant.isOpen !== false
                    ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                    : "bg-gray-100 text-gray-600 border-gray-200"
                )}
              >
                {restaurant.isOpen !== false
                  ? locale === "ar"
                    ? "مفتوح الآن"
                    : "Open Now"
                  : locale === "ar"
                  ? "مغلق"
                  : "Closed"}
              </Badge>
              {displayCategory && (
                <Badge variant="outline" className="bg-gray-50 text-gray-600 border-gray-200">
                  {displayCategory}
                </Badge>
              )}
            </div>

            {/* Restaurant Name */}
            <h1 className="mb-2 text-2xl font-bold text-gray-900 md:text-3xl">
              {displayName}
            </h1>

            {/* Description */}
            {displayDescription && (
              <p className="mb-4 text-gray-500 line-clamp-2">
                {displayDescription}
              </p>
            )}

            {/* Rating & Delivery Info Row */}
            <div className="flex flex-wrap items-center gap-4 text-sm">
              {/* Rating with Gold Stars */}
              {restaurant.rating && (
                <div className="flex items-center gap-1.5">
                  <div className="flex items-center gap-0.5">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        className={cn(
                          "h-4 w-4",
                          star <= Math.floor(restaurant.rating!)
                            ? "fill-amber-400 text-amber-400"
                            : "fill-gray-200 text-gray-200"
                        )}
                      />
                    ))}
                  </div>
                  <span className="font-bold text-gray-900">{restaurant.rating}</span>
                  {restaurant.reviewCount && (
                    <span className="text-gray-400">
                      ({restaurant.reviewCount})
                    </span>
                  )}
                </div>
              )}

              {/* Delivery Time */}
              {restaurant.deliveryTime && (
                <div className="flex items-center gap-1.5 text-gray-500">
                  <Clock className="h-4 w-4 text-emerald-500" />
                  <span>
                    {restaurant.deliveryTime.min}-{restaurant.deliveryTime.max}{" "}
                    {locale === "ar" ? "دقيقة" : "min"}
                  </span>
                </div>
              )}

              {/* Price Range */}
              {restaurant.priceRange && (
                <span className="font-semibold text-emerald-600">
                  {restaurant.priceRange}
                </span>
              )}
            </div>

            {/* Divider */}
            <div className="my-5 h-px bg-gray-100" />

            {/* Info Section: Hours, Address, Phone */}
            <div className="grid gap-4 sm:grid-cols-3">
              {/* Working Hours */}
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-emerald-50">
                  <Clock className="h-5 w-5 text-emerald-600" />
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                    {locale === "ar" ? "ساعات العمل" : "Hours"}
                  </p>
                  <p className="font-medium text-gray-900">
                    {getWorkingHoursDisplay()}
                  </p>
                </div>
              </div>

              {/* Address */}
              {restaurant.address && (
                <div className="flex items-start gap-3">
                  <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-emerald-50">
                    <MapPin className="h-5 w-5 text-emerald-600" />
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                      {locale === "ar" ? "العنوان" : "Address"}
                    </p>
                    <p className="font-medium text-gray-900 line-clamp-1">
                      {restaurant.address}
                    </p>
                  </div>
                </div>
              )}

              {/* Phone */}
              {restaurant.phone && (
                <div className="flex items-start gap-3">
                  <a href={`tel:${restaurant.phone}`} className="flex items-start gap-3 group">
                    <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-emerald-50 transition-colors group-hover:bg-emerald-100">
                      <Phone className="h-5 w-5 text-emerald-600" />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                        {locale === "ar" ? "الهاتف" : "Phone"}
                      </p>
                      <p className="font-medium text-emerald-600 group-hover:text-emerald-700">
                        {restaurant.phone}
                      </p>
                    </div>
                  </a>
                </div>
              )}
            </div>

            {/* Delivery Info Cards */}
            <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {/* Delivery Fee */}
              <div className="rounded-xl bg-gray-50 p-3 text-center">
                <Bike className="mx-auto mb-1 h-5 w-5 text-emerald-500" />
                <p className="text-xs text-gray-400">
                  {locale === "ar" ? "رسوم التوصيل" : "Delivery Fee"}
                </p>
                <p className="font-bold text-gray-900">
                  {restaurant.deliveryFee
                    ? formatPrice(restaurant.deliveryFee)
                    : locale === "ar"
                    ? "مجاني"
                    : "Free"}
                </p>
              </div>

              {/* Minimum Order */}
              <div className="rounded-xl bg-gray-50 p-3 text-center">
                <DollarSign className="mx-auto mb-1 h-5 w-5 text-emerald-500" />
                <p className="text-xs text-gray-400">
                  {locale === "ar" ? "الحد الأدنى" : "Min. Order"}
                </p>
                <p className="font-bold text-gray-900">
                  {restaurant.minimumOrder
                    ? formatPrice(restaurant.minimumOrder)
                    : formatPrice(0)}
                </p>
              </div>

              {/* Delivery Time */}
              <div className="rounded-xl bg-gray-50 p-3 text-center">
                <Clock className="mx-auto mb-1 h-5 w-5 text-emerald-500" />
                <p className="text-xs text-gray-400">
                  {locale === "ar" ? "وقت التوصيل" : "Delivery"}
                </p>
                <p className="font-bold text-gray-900">
                  {restaurant.deliveryTime
                    ? `${restaurant.deliveryTime.min}-${restaurant.deliveryTime.max} ${locale === "ar" ? "د" : "min"}`
                    : locale === "ar"
                    ? "25-35 د"
                    : "25-35 min"}
                </p>
              </div>

              {/* Rating */}
              <div className="rounded-xl bg-gray-50 p-3 text-center">
                <Star className="mx-auto mb-1 h-5 w-5 fill-amber-400 text-amber-400" />
                <p className="text-xs text-gray-400">
                  {locale === "ar" ? "التقييم" : "Rating"}
                </p>
                <p className="font-bold text-gray-900">
                  {restaurant.rating || "4.5"}
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Menu Section */}
      <div className="container mx-auto px-4 py-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-6"
        >
          <h2 className="text-xl font-bold text-gray-900 md:text-2xl">
            {locale === "ar" ? "قائمة الطعام" : "Menu"}
          </h2>
        </motion.div>

        {/* Menu Content */}
        {isLoadingMenu ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
          </div>
        ) : menu && menu.categories && menu.categories.length > 0 ? (
          <MenuSection
            menu={menu}
            restaurantId={String(restaurant.id)}
            restaurantName={restaurant.name}
            restaurantNameAr={nameAr}
          />
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-gray-100">
              <Info className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="mb-2 text-lg font-semibold text-gray-900">
              {locale === "ar" ? "لا توجد قائمة متاحة" : "No menu available"}
            </h3>
            <p className="text-gray-500">
              {locale === "ar"
                ? "سيتم إضافة القائمة قريباً"
                : "Menu will be added soon"}
            </p>
          </div>
        )}
      </div>

      {/* Sticky Cart Bar */}
      {cartItemsCount > 0 && (
        <motion.div
          initial={{ y: 100 }}
          animate={{ y: 0 }}
          className="fixed bottom-0 inset-x-0 z-40 border-t border-gray-200 bg-white/95 backdrop-blur-lg shadow-[0_-4px_20px_rgba(0,0,0,0.08)]"
        >
          <div className="container mx-auto px-4 py-4">
            <Link href={`/${locale}/cart`}>
              <Button
                className={cn(
                  "w-full h-14 rounded-2xl text-base font-semibold",
                  "bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700",
                  "shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40",
                  "transition-all duration-300"
                )}
                size="lg"
              >
                <ShoppingCart className={cn("h-5 w-5", isRTL ? "ml-2" : "mr-2")} />
                <span className="flex items-center gap-2">
                  <span className="flex h-6 min-w-[24px] items-center justify-center rounded-full bg-white/20 px-2 text-sm">
                    {cartItemsCount}
                  </span>
                  <span>{locale === "ar" ? "عرض السلة" : "View Cart"}</span>
                </span>
                <span className={cn("font-bold", isRTL ? "mr-auto" : "ml-auto")}>
                  {formatPrice(cartTotal)}
                </span>
                {isRTL ? (
                  <ChevronLeft className="h-5 w-5" />
                ) : (
                  <ChevronRight className="h-5 w-5" />
                )}
              </Button>
            </Link>
          </div>
        </motion.div>
      )}
    </div>
  );
}
