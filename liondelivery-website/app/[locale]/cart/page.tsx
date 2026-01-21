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
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useCartStore, CartItem } from "@/lib/stores/cart-store";
import { formatPrice } from "@/lib/utils/formatters";

export default function CartPage() {
  const locale = useLocale();
  const t = useTranslations("cart");

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
      <div className="min-h-screen bg-background py-20">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mx-auto max-w-md"
          >
            <div className="mb-6 flex justify-center">
              <div className="flex h-24 w-24 items-center justify-center rounded-full bg-secondary-800">
                <ShoppingBag className="h-12 w-12 text-muted-foreground" />
              </div>
            </div>
            <h1 className="mb-3 text-2xl font-bold">{t("empty")}</h1>
            <p className="mb-8 text-muted-foreground">{t("emptyDescription")}</p>
            <Button asChild size="lg">
              <Link href={`/${locale}/restaurants`}>
                {t("browseRestaurants")}
                {locale === "ar" ? (
                  <ChevronLeft className="ml-2 h-4 w-4" />
                ) : (
                  <ChevronRight className="ml-2 h-4 w-4" />
                )}
              </Link>
            </Button>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-8">
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
                <h1 className="text-2xl font-bold">🛒 {t("title")}</h1>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearCart}
                  className="text-error-500 hover:text-error-600"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  {t("clearAll")}
                </Button>
              </div>

              {/* Restaurant Name */}
              {displayRestaurantName && (
                <div className="mb-4 rounded-xl bg-secondary-800 p-4">
                  <p className="text-sm text-muted-foreground">
                    {locale === "ar" ? "من:" : "From:"}
                  </p>
                  <p className="font-semibold">{displayRestaurantName}</p>
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
              <div className="mt-6">
                <h3 className="mb-3 font-semibold">{t("notes")}</h3>
                <Textarea
                  value={notes}
                  onChange={(e) => setOrderNotes(e.target.value)}
                  placeholder={t("notesPlaceholder")}
                  rows={3}
                />
              </div>

              {/* Add More */}
              {restaurantId && (
                <div className="mt-6">
                  <Link href={`/${locale}/restaurants/${restaurantId}`}>
                    <Button variant="outline" className="w-full">
                      <Plus className="mr-2 h-4 w-4" />
                      {locale === "ar"
                        ? `أضف المزيد من ${displayRestaurantName}`
                        : `Add more from ${displayRestaurantName}`}
                    </Button>
                  </Link>
                </div>
              )}
            </motion.div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="sticky top-24 rounded-2xl bg-secondary-800 p-6"
            >
              <h2 className="mb-4 text-lg font-semibold">
                {locale === "ar" ? "ملخص الطلب" : "Order Summary"}
              </h2>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">{t("subtotal")}</span>
                  <span>{formatPrice(getSubtotal())}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">{t("delivery")}</span>
                  <span>{formatPrice(getDeliveryFee())}</span>
                </div>
                <div className="border-t border-border pt-3">
                  <div className="flex justify-between text-base font-semibold">
                    <span>{t("total")}</span>
                    <span className="text-primary-500">{formatPrice(getTotal())}</span>
                  </div>
                </div>
              </div>

              <Button asChild className="mt-6 w-full" size="lg">
                <Link href={`/${locale}/checkout`}>
                  {t("checkout")}
                  <ArrowRight className="ms-2 h-4 w-4" />
                </Link>
              </Button>
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
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="flex gap-4 rounded-2xl bg-secondary-800 p-4"
    >
      {/* Image */}
      {item.image ? (
        <div className="relative h-24 w-24 flex-shrink-0 overflow-hidden rounded-xl">
          <Image src={item.image} alt={displayName} fill className="object-cover" />
        </div>
      ) : (
        <div className="flex h-24 w-24 flex-shrink-0 items-center justify-center rounded-xl bg-secondary-700 text-4xl">
          🍽️
        </div>
      )}

      {/* Content */}
      <div className="flex flex-1 flex-col">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold">{displayName}</h3>
            {displayVariant && (
              <p className="text-sm text-muted-foreground">{displayVariant}</p>
            )}
            {item.addons && item.addons.length > 0 && (
              <p className="text-xs text-muted-foreground">
                +{" "}
                {item.addons
                  .map((a) => (locale === "ar" && a.nameAr ? a.nameAr : a.name))
                  .join(", ")}
              </p>
            )}
            {item.notes && (
              <p className="text-xs text-primary-500">📝 {item.notes}</p>
            )}
          </div>
          <button
            onClick={() => onRemove(item.id)}
            className="text-muted-foreground transition-colors hover:text-error-500"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>

        <div className="mt-auto flex items-center justify-between pt-3">
          {/* Quantity Controls */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => onUpdateQuantity(item.id, item.quantity - 1)}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary-700 text-foreground transition-colors hover:bg-secondary-600"
            >
              <Minus className="h-4 w-4" />
            </button>
            <span className="w-6 text-center font-medium">{item.quantity}</span>
            <button
              onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-500 text-white transition-colors hover:bg-primary-600"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          {/* Price */}
          <span className="font-semibold text-primary-500">
            {formatPrice(itemPrice * item.quantity)}
          </span>
        </div>
      </div>
    </motion.div>
  );
}
