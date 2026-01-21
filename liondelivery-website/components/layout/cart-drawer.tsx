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
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: locale === "ar" ? "-100%" : "100%" }}
            animate={{ x: 0 }}
            exit={{ x: locale === "ar" ? "-100%" : "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className={`fixed inset-y-0 z-50 flex w-full max-w-md flex-col bg-secondary-900 shadow-xl ${
              locale === "ar" ? "left-0" : "right-0"
            }`}
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-border p-4">
              <div className="flex items-center gap-2">
                <ShoppingBag className="h-5 w-5 text-primary-500" />
                <h2 className="text-lg font-semibold">{t("title")}</h2>
              </div>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-5 w-5" />
              </Button>
            </div>

            {items.length === 0 ? (
              /* Empty State */
              <div className="flex flex-1 flex-col items-center justify-center p-8 text-center">
                <div className="mb-4 rounded-full bg-secondary-800 p-6">
                  <ShoppingBag className="h-12 w-12 text-muted-foreground" />
                </div>
                <h3 className="mb-2 text-lg font-semibold">{t("empty")}</h3>
                <p className="mb-6 text-sm text-muted-foreground">
                  {t("emptyDescription")}
                </p>
                <Button onClick={onClose} asChild>
                  <Link href={`/${locale}/restaurants`}>
                    {t("browseRestaurants")}
                  </Link>
                </Button>
              </div>
            ) : (
              <>
                {/* Restaurant Name */}
                {displayRestaurantName && (
                  <div className="border-b border-border bg-secondary-800/50 px-4 py-3">
                    <p className="text-sm text-muted-foreground">
                      {locale === "ar" ? "من:" : "From:"}
                    </p>
                    <p className="font-medium">{displayRestaurantName}</p>
                  </div>
                )}

                {/* Cart Items */}
                <div className="flex-1 overflow-y-auto p-4">
                  <ul className="space-y-4">
                    {items.map((item) => (
                      <CartItemCard
                        key={item.id}
                        item={item}
                        locale={locale}
                        onUpdateQuantity={updateQuantity}
                        onRemove={removeItem}
                      />
                    ))}
                  </ul>
                </div>

                {/* Footer */}
                <div className="border-t border-border bg-secondary-800/50 p-4 space-y-4">
                  {/* Summary */}
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">{t("subtotal")}</span>
                      <span>{formatPrice(getSubtotal())}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">{t("delivery")}</span>
                      <span>{formatPrice(getDeliveryFee())}</span>
                    </div>
                    <div className="flex justify-between border-t border-border pt-2 text-base font-semibold">
                      <span>{t("total")}</span>
                      <span className="text-primary-500">{formatPrice(getTotal())}</span>
                    </div>
                  </div>

                  {/* Checkout Button */}
                  <Button className="w-full" size="lg" asChild onClick={onClose}>
                    <Link href={`/${locale}/checkout`}>
                      {t("checkout")} • {formatPrice(getTotal())}
                    </Link>
                  </Button>

                  {/* Continue Shopping */}
                  <Button
                    variant="outline"
                    className="w-full"
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
  onUpdateQuantity: (id: string, quantity: number) => void;
  onRemove: (id: string) => void;
}

function CartItemCard({ item, locale, onUpdateQuantity, onRemove }: CartItemCardProps) {
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
      exit={{ opacity: 0, x: -100 }}
      className="flex gap-3 rounded-xl bg-secondary-800 p-3"
    >
      {/* Image */}
      {item.image && (
        <div className="relative h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg">
          <Image
            src={item.image}
            alt={displayName}
            fill
            className="object-cover"
          />
        </div>
      )}

      {/* Content */}
      <div className="flex flex-1 flex-col">
        <div className="flex items-start justify-between">
          <div>
            <h4 className="font-medium line-clamp-1">{displayName}</h4>
            {displayVariant && (
              <p className="text-xs text-muted-foreground">{displayVariant}</p>
            )}
            {item.addons && item.addons.length > 0 && (
              <p className="text-xs text-muted-foreground">
                + {item.addons.map((a) => (locale === "ar" && a.nameAr ? a.nameAr : a.name)).join(", ")}
              </p>
            )}
            {item.notes && (
              <p className="text-xs text-primary-500 line-clamp-1">
                📝 {item.notes}
              </p>
            )}
          </div>
          <button
            onClick={() => onRemove(item.id)}
            className="text-muted-foreground transition-colors hover:text-error-500"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>

        <div className="mt-auto flex items-center justify-between pt-2">
          {/* Quantity Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => onUpdateQuantity(item.id, item.quantity - 1)}
              className="flex h-7 w-7 items-center justify-center rounded-full bg-secondary-700 text-foreground transition-colors hover:bg-secondary-600"
            >
              <Minus className="h-3 w-3" />
            </button>
            <span className="w-6 text-center text-sm font-medium">
              {item.quantity}
            </span>
            <button
              onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
              className="flex h-7 w-7 items-center justify-center rounded-full bg-primary-500 text-white transition-colors hover:bg-primary-600"
            >
              <Plus className="h-3 w-3" />
            </button>
          </div>

          {/* Price */}
          <span className="font-semibold text-primary-500">
            {formatPrice(itemPrice * item.quantity)}
          </span>
        </div>
      </div>
    </motion.li>
  );
}
