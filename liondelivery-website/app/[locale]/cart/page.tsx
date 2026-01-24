"use client";

import Link from "next/link";
import Image from "next/image";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import {
  Minus,
  Plus,
  Trash2,
  ShoppingBag,
  ChevronLeft,
  ChevronRight,
  ArrowRight,
  ArrowLeft,
  Store,
  StickyNote,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useCartStore, CartItem } from "@/lib/stores/cart-store";
import { formatPrice } from "@/lib/utils/formatters";
import { cn } from "@/lib/utils/cn";

export default function CartPage() {
  const locale = useLocale();
  const t = useTranslations("cart");
  const isRTL = locale === "ar";

  const {
    items,
    restaurantName,
    restaurantNameAr,
    restaurantId,
    notes,
    updateQuantity,
    removeItem,
    setOrderNotes,
    clearCart,
    getSubtotal,
    getDeliveryFee,
    getTotal,
  } = useCartStore();

  const displayRestaurantName =
    locale === "ar" && restaurantNameAr ? restaurantNameAr : restaurantName;

  if (items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-20">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mx-auto max-w-md"
          >
            {/* Empty Cart Illustration */}
            <div className="mb-8 flex justify-center">
              <div className="relative">
                <div className="flex h-32 w-32 items-center justify-center rounded-full bg-emerald-100">
                  <ShoppingBag className="h-16 w-16 text-emerald-500" />
                </div>
                <div className="absolute -bottom-2 -right-2 flex h-12 w-12 items-center justify-center rounded-full bg-white shadow-lg">
                  <span className="text-2xl">?</span>
                </div>
              </div>
            </div>

            <h1 className="mb-3 text-2xl font-bold text-gray-900">{t("empty")}</h1>
            <p className="mb-8 text-gray-500">{t("emptyDescription")}</p>

            {/* Continue Shopping Button */}
            <Button
              asChild
              size="lg"
              className="bg-emerald-500 px-8 text-white shadow-lg shadow-emerald-500/30 hover:bg-emerald-600 hover:shadow-xl hover:shadow-emerald-500/40"
            >
              <Link href={`/${locale}/restaurants`} className="inline-flex items-center gap-2">
                {t("browseRestaurants")}
                {isRTL ? (
                  <ChevronLeft className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
              </Link>
            </Button>

            {/* Continue Shopping Link */}
            <div className="mt-6">
              <Link
                href={`/${locale}`}
                className="inline-flex items-center gap-1 text-sm text-emerald-600 transition-colors hover:text-emerald-700"
              >
                {isRTL ? <ArrowRight className="h-4 w-4" /> : <ArrowLeft className="h-4 w-4" />}
                {isRTL ? "العودة للرئيسية" : "Continue Shopping"}
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Cart Items */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {/* Header */}
              <div className="mb-6 flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{t("title")}</h1>
                  <p className="mt-1 text-sm text-gray-500">
                    {items.length} {isRTL ? "عنصر" : items.length === 1 ? "item" : "items"}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearCart}
                  className="text-red-500 hover:bg-red-50 hover:text-red-600"
                >
                  <Trash2 className={cn("h-4 w-4", isRTL ? "ml-2" : "mr-2")} />
                  {t("clearAll")}
                </Button>
              </div>

              {/* Restaurant Name */}
              {displayRestaurantName && (
                <div className="mb-4 flex items-center gap-3 rounded-xl bg-white p-4 shadow-sm">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100">
                    <Store className="h-5 w-5 text-emerald-600" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">
                      {isRTL ? "الطلب من:" : "Ordering from:"}
                    </p>
                    <p className="font-semibold text-gray-900">{displayRestaurantName}</p>
                  </div>
                </div>
              )}

              {/* Cart Items */}
              <div className="space-y-4">
                {items.map((item, index) => (
                  <CartItemCard
                    key={item.id}
                    item={item}
                    locale={locale}
                    index={index}
                    onUpdateQuantity={updateQuantity}
                    onRemove={removeItem}
                  />
                ))}
              </div>

              {/* Order Notes */}
              <div className="mt-6 rounded-xl bg-white p-4 shadow-sm">
                <div className="mb-3 flex items-center gap-2">
                  <StickyNote className="h-5 w-5 text-emerald-600" />
                  <h3 className="font-semibold text-gray-900">{t("notes")}</h3>
                </div>
                <Textarea
                  value={notes}
                  onChange={(e) => setOrderNotes(e.target.value)}
                  placeholder={t("notesPlaceholder")}
                  rows={3}
                  className="border-gray-200 bg-gray-50 focus:border-emerald-500 focus:bg-white focus:ring-emerald-500"
                />
              </div>

              {/* Add More */}
              {restaurantId && (
                <div className="mt-6">
                  <Link href={`/${locale}/restaurants/${restaurantId}`}>
                    <Button
                      variant="outline"
                      className="w-full border-2 border-dashed border-emerald-300 bg-emerald-50/50 text-emerald-700 hover:border-emerald-500 hover:bg-emerald-100"
                    >
                      <Plus className={cn("h-4 w-4", isRTL ? "ml-2" : "mr-2")} />
                      {isRTL
                        ? `اضف المزيد من ${displayRestaurantName}`
                        : `Add more from ${displayRestaurantName}`}
                    </Button>
                  </Link>
                </div>
              )}

              {/* Continue Shopping Link */}
              <div className="mt-6 text-center">
                <Link
                  href={`/${locale}/restaurants`}
                  className="inline-flex items-center gap-1 text-sm text-gray-500 transition-colors hover:text-emerald-600"
                >
                  {isRTL ? <ArrowRight className="h-4 w-4" /> : <ArrowLeft className="h-4 w-4" />}
                  {isRTL ? "تصفح المزيد من المطاعم" : "Browse more restaurants"}
                </Link>
              </div>
            </motion.div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="sticky top-24 rounded-2xl bg-white p-6 shadow-sm"
            >
              <h2 className="mb-4 text-lg font-semibold text-gray-900">
                {isRTL ? "ملخص الطلب" : "Order Summary"}
              </h2>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">{t("subtotal")}</span>
                  <span className="text-gray-900">{formatPrice(getSubtotal())}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">{t("delivery")}</span>
                  <span className="text-gray-900">{formatPrice(getDeliveryFee())}</span>
                </div>
                <div className="border-t border-gray-100 pt-3">
                  <div className="flex justify-between text-base">
                    <span className="font-semibold text-gray-900">{t("total")}</span>
                    <span className="font-bold text-emerald-600">{formatPrice(getTotal())}</span>
                  </div>
                </div>
              </div>

              <Button
                asChild
                className="mt-6 h-14 w-full bg-emerald-500 text-base font-semibold text-white shadow-lg shadow-emerald-500/30 transition-all hover:bg-emerald-600 hover:shadow-xl hover:shadow-emerald-500/40"
                size="lg"
              >
                <Link href={`/${locale}/checkout`} className="inline-flex items-center justify-center gap-2">
                  {t("checkout")}
                  {isRTL ? (
                    <ArrowLeft className="h-5 w-5" />
                  ) : (
                    <ArrowRight className="h-5 w-5" />
                  )}
                </Link>
              </Button>

              {/* Secure Checkout Note */}
              <p className="mt-4 text-center text-xs text-gray-400">
                {isRTL ? "الدفع عند الاستلام متاح" : "Cash on delivery available"}
              </p>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}

interface CartItemCardProps {
  item: CartItem;
  locale: string;
  index: number;
  onUpdateQuantity: (id: string, quantity: number) => void;
  onRemove: (id: string) => void;
}

function CartItemCard({
  item,
  locale,
  index,
  onUpdateQuantity,
  onRemove,
}: CartItemCardProps) {
  const isRTL = locale === "ar";
  const displayName = locale === "ar" && item.nameAr ? item.nameAr : item.name;
  const displayVariant = item.variant
    ? locale === "ar" && item.variant.nameAr
      ? item.variant.nameAr
      : item.variant.name
    : null;

  // Calculate item total
  let itemPrice = item.variant?.price || item.price;
  if (item.addons) {
    itemPrice += item.addons.reduce(
      (sum, addon) => sum + addon.price * addon.quantity,
      0
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: isRTL ? 20 : -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="flex gap-4 rounded-xl bg-white p-4 shadow-sm"
    >
      {/* Image */}
      {item.image ? (
        <div className="relative h-24 w-24 flex-shrink-0 overflow-hidden rounded-xl">
          <Image src={item.image} alt={displayName} fill className="object-cover" />
        </div>
      ) : (
        <div className="flex h-24 w-24 flex-shrink-0 items-center justify-center rounded-xl bg-gray-100">
          <ShoppingBag className="h-8 w-8 text-gray-400" />
        </div>
      )}

      {/* Content */}
      <div className="flex flex-1 flex-col">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">{displayName}</h3>
            {displayVariant && (
              <p className="text-sm text-gray-500">{displayVariant}</p>
            )}
            {item.addons && item.addons.length > 0 && (
              <p className="text-xs text-gray-400">
                +{" "}
                {item.addons
                  .map((a) => (locale === "ar" && a.nameAr ? a.nameAr : a.name))
                  .join(", ")}
              </p>
            )}
            {item.notes && (
              <p className="mt-1 text-xs text-emerald-600">
                <StickyNote className="mr-1 inline h-3 w-3" />
                {item.notes}
              </p>
            )}
          </div>
          <button
            onClick={() => onRemove(item.id)}
            className="rounded-full p-1 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-500"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>

        <div className="mt-auto flex items-center justify-between pt-3">
          {/* Quantity Controls */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => onUpdateQuantity(item.id, item.quantity - 1)}
              className="flex h-9 w-9 items-center justify-center rounded-full border-2 border-gray-200 bg-white text-gray-600 transition-all hover:border-gray-300 hover:bg-gray-50"
            >
              <Minus className="h-4 w-4" />
            </button>
            <span className="w-10 text-center text-base font-semibold text-gray-900">
              {item.quantity}
            </span>
            <button
              onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
              className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-500 text-white shadow-md shadow-emerald-500/30 transition-all hover:bg-emerald-600 hover:shadow-lg hover:shadow-emerald-500/40"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          {/* Price */}
          <span className="text-lg font-bold text-emerald-600">
            {formatPrice(itemPrice * item.quantity)}
          </span>
        </div>
      </div>
    </motion.div>
  );
}
