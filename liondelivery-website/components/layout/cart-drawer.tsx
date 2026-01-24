"use client";

import Link from "next/link";
import Image from "next/image";
import { useLocale, useTranslations } from "next-intl";
import { X, Minus, Plus, Trash2, ShoppingBag } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useCartStore, CartItem } from "@/lib/stores/cart-store";
import { formatPrice } from "@/lib/utils/formatters";

interface CartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CartDrawer({ isOpen, onClose }: CartDrawerProps) {
  const t = useTranslations("cart");
  const locale = useLocale();
  const {
    items,
    restaurantName,
    restaurantNameAr,
    updateQuantity,
    removeItem,
    getSubtotal,
    getDeliveryFee,
    getTotal,
  } = useCartStore();

  const displayRestaurantName = locale === "ar" && restaurantNameAr ? restaurantNameAr : restaurantName;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-secondary-900/20 backdrop-blur-sm"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: locale === "ar" ? "-100%" : "100%" }}
            animate={{ x: 0 }}
            exit={{ x: locale === "ar" ? "-100%" : "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className={`fixed inset-y-0 z-50 flex w-full max-w-md flex-col bg-white shadow-elevated ${
              locale === "ar" ? "left-0" : "right-0"
            }`}
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-secondary-100 p-4">
              <div className="flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 text-primary-500">
                  <ShoppingBag className="h-5 w-5" />
                </span>
                <div>
                  <h2 className="text-lg font-semibold text-secondary-900">{t("title")}</h2>
                  {items.length > 0 && (
                    <p className="text-xs text-secondary-500">
                      {items.length} {locale === "ar" ? "عناصر" : "items"}
                    </p>
                  )}
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-9 w-9 rounded-full text-secondary-500 hover:text-secondary-700 hover:bg-secondary-100"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>

            {items.length === 0 ? (
              /* Empty State */
              <div className="flex flex-1 flex-col items-center justify-center p-8 text-center">
                <div className="mb-5 flex h-24 w-24 items-center justify-center rounded-full bg-secondary-50">
                  <ShoppingBag className="h-12 w-12 text-secondary-300" />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-secondary-900">{t("empty")}</h3>
                <p className="mb-6 max-w-xs text-sm text-secondary-500">
                  {t("emptyDescription")}
                </p>
                <Button
                  onClick={onClose}
                  asChild
                  className="bg-primary-500 hover:bg-primary-600 text-white shadow-primary rounded-xl px-6"
                >
                  <Link href={`/${locale}/restaurants`}>
                    {t("browseRestaurants")}
                  </Link>
                </Button>
              </div>
            ) : (
              <>
                {/* Restaurant Name */}
                {displayRestaurantName && (
                  <div className="border-b border-secondary-100 bg-secondary-50/50 px-4 py-3">
                    <p className="text-xs text-secondary-500">
                      {locale === "ar" ? "من:" : "From:"}
                    </p>
                    <p className="font-medium text-secondary-800">{displayRestaurantName}</p>
                  </div>
                )}

                {/* Cart Items */}
                <div className="flex-1 overflow-y-auto p-4 scrollbar-thin">
                  <ul className="space-y-3">
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
                  </ul>
                </div>

                {/* Footer */}
                <div className="border-t border-secondary-100 bg-white p-4 space-y-4">
                  {/* Summary */}
                  <div className="space-y-2.5 text-sm">
                    <div className="flex justify-between">
                      <span className="text-secondary-600">{t("subtotal")}</span>
                      <span className="font-medium text-secondary-800">{formatPrice(getSubtotal())}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-secondary-600">{t("delivery")}</span>
                      <span className="font-medium text-secondary-800">{formatPrice(getDeliveryFee())}</span>
                    </div>
                    <div className="divider my-2" />
                    <div className="flex justify-between text-base font-semibold">
                      <span className="text-secondary-900">{t("total")}</span>
                      <span className="text-primary-500">{formatPrice(getTotal())}</span>
                    </div>
                  </div>

                  {/* Checkout Button */}
                  <Button
                    className="w-full bg-primary-500 hover:bg-primary-600 text-white shadow-primary hover:shadow-primary-lg transition-all rounded-xl h-12 text-base font-semibold btn-press"
                    size="lg"
                    asChild
                    onClick={onClose}
                  >
                    <Link href={`/${locale}/checkout`}>
                      {t("checkout")} - {formatPrice(getTotal())}
                    </Link>
                  </Button>

                  {/* Continue Shopping */}
                  <Button
                    variant="ghost"
                    className="w-full text-secondary-600 hover:text-secondary-800 hover:bg-secondary-50 rounded-xl"
                    onClick={onClose}
                  >
                    {t("continueShopping")}
                  </Button>
                </div>
              </>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

interface CartItemCardProps {
  item: CartItem;
  locale: string;
  index: number;
  onUpdateQuantity: (id: string, quantity: number) => void;
  onRemove: (id: string) => void;
}

function CartItemCard({ item, locale, index, onUpdateQuantity, onRemove }: CartItemCardProps) {
  const displayName = locale === "ar" && item.nameAr ? item.nameAr : item.name;
  const displayVariant = item.variant
    ? locale === "ar" && item.variant.nameAr
      ? item.variant.nameAr
      : item.variant.name
    : null;

  // Calculate item total
  let itemPrice = item.variant?.price || item.price;
  if (item.addons) {
    itemPrice += item.addons.reduce((sum, addon) => sum + addon.price * addon.quantity, 0);
  }

  return (
    <motion.li
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: locale === "ar" ? 100 : -100 }}
      transition={{ delay: index * 0.05 }}
      className="group rounded-xl bg-secondary-50 p-3 transition-all hover:bg-secondary-100/80"
    >
      <div className="flex gap-3">
        {/* Image */}
        {item.image && (
          <div className="relative h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg shadow-soft">
            <Image
              src={item.image}
              alt={displayName}
              fill
              className="object-cover"
            />
          </div>
        )}

        {/* Content */}
        <div className="flex flex-1 flex-col min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <h4 className="font-medium text-secondary-900 line-clamp-1">{displayName}</h4>
              {displayVariant && (
                <p className="text-xs text-secondary-500 mt-0.5">{displayVariant}</p>
              )}
              {item.addons && item.addons.length > 0 && (
                <p className="text-xs text-secondary-500 line-clamp-1 mt-0.5">
                  + {item.addons.map((a) => (locale === "ar" && a.nameAr ? a.nameAr : a.name)).join(", ")}
                </p>
              )}
              {item.notes && (
                <p className="text-xs text-primary-600 line-clamp-1 mt-1">
                  {item.notes}
                </p>
              )}
            </div>
            <button
              onClick={() => onRemove(item.id)}
              className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-secondary-400 opacity-0 group-hover:opacity-100 transition-all hover:bg-error-50 hover:text-error-500"
              aria-label="Remove item"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-auto flex items-center justify-between pt-2">
            {/* Quantity Controls */}
            <div className="flex items-center gap-1">
              <button
                onClick={() => onUpdateQuantity(item.id, item.quantity - 1)}
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-secondary-600 shadow-soft transition-all hover:bg-secondary-100 hover:shadow-md btn-press"
                aria-label="Decrease quantity"
              >
                <Minus className="h-3.5 w-3.5" />
              </button>
              <span className="w-8 text-center text-sm font-semibold text-secondary-900">
                {item.quantity}
              </span>
              <button
                onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-500 text-white shadow-primary transition-all hover:bg-primary-600 hover:shadow-primary-lg btn-press"
                aria-label="Increase quantity"
              >
                <Plus className="h-3.5 w-3.5" />
              </button>
            </div>

            {/* Price */}
            <span className="font-semibold text-primary-500">
              {formatPrice(itemPrice * item.quantity)}
            </span>
          </div>
        </div>
      </div>
    </motion.li>
  );
}
