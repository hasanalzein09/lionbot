"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { useLocale, useTranslations } from "next-intl";
import { motion, AnimatePresence } from "framer-motion";
import { X, Minus, Plus, Check, ShoppingCart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useCartStore } from "@/lib/stores/cart-store";
import { formatPrice } from "@/lib/utils/formatters";
import { cn } from "@/lib/utils/cn";
import type { MenuItem, MenuItemVariant, MenuItemAddon } from "@/types/menu";

interface MenuItemModalProps {
  item: MenuItem | null;
  isOpen: boolean;
  onClose: () => void;
  restaurantId: string;
  restaurantName: string;
  restaurantNameAr?: string;
}

export function MenuItemModal({
  item,
  isOpen,
  onClose,
  restaurantId,
  restaurantName,
  restaurantNameAr,
}: MenuItemModalProps) {
  const locale = useLocale();
  const isRTL = locale === "ar";
  const t = useTranslations("menu");
  const addItem = useCartStore((state) => state.addItem);

  const [selectedVariant, setSelectedVariant] = useState<MenuItemVariant | null>(null);
  const [selectedAddons, setSelectedAddons] = useState<Map<string, number>>(new Map());
  const [quantity, setQuantity] = useState(1);
  const [notes, setNotes] = useState("");

  // Reset state when item changes
  useEffect(() => {
    if (item) {
      // Select default variant if available
      const defaultVariant = item.variants?.find((v) => v.isDefault) || item.variants?.[0];
      setSelectedVariant(defaultVariant || null);
      setSelectedAddons(new Map());
      setQuantity(1);
      setNotes("");
    }
  }, [item]);

  if (!item) return null;

  // Handle both camelCase and snake_case from API
  const nameAr = item.nameAr || item.name_ar;
  const descriptionAr = item.descriptionAr || item.description_ar;
  const price = item.price ?? item.price_min ?? 0;
  const isAvailable = item.isAvailable ?? item.is_available ?? true;

  const displayName = locale === "ar" && nameAr ? nameAr : item.name;
  const displayDescription =
    locale === "ar" && descriptionAr ? descriptionAr : item.description;

  // Calculate total price
  const basePrice = selectedVariant?.price || price;
  const addonsTotal = Array.from(selectedAddons.entries()).reduce(
    (total, [addonId, qty]) => {
      const addon = item.addons?.find((a) => String(a.id) === addonId);
      return total + (addon?.price || 0) * qty;
    },
    0
  );
  const itemTotal = (basePrice + addonsTotal) * quantity;

  const toggleAddon = (addon: MenuItemAddon) => {
    const addonId = String(addon.id);
    const newAddons = new Map(selectedAddons);
    if (newAddons.has(addonId)) {
      newAddons.delete(addonId);
    } else {
      newAddons.set(addonId, 1);
    }
    setSelectedAddons(newAddons);
  };

  const handleAddToCart = () => {
    const cartAddons = item.addons
      ?.filter((addon) => selectedAddons.has(String(addon.id)))
      .map((addon) => ({
        id: String(addon.id),
        name: addon.name,
        nameAr: addon.nameAr || addon.name_ar,
        price: addon.price,
        quantity: selectedAddons.get(String(addon.id)) || 1,
      }));

    addItem({
      productId: String(item.id),
      name: item.name,
      nameAr: nameAr,
      description: item.description,
      image: item.image,
      price: price,
      quantity,
      variant: selectedVariant
        ? {
            id: String(selectedVariant.id),
            name: selectedVariant.name,
            nameAr: selectedVariant.nameAr || selectedVariant.name_ar,
            price: selectedVariant.price,
          }
        : undefined,
      addons: cartAddons,
      notes: notes || undefined,
      restaurantId,
      restaurantName,
      restaurantNameAr,
    });

    onClose();
  };

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
            className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className={cn(
              "fixed inset-x-4 bottom-4 top-4 z-50 mx-auto flex max-w-lg flex-col overflow-hidden rounded-3xl bg-white shadow-2xl",
              "md:inset-auto md:left-1/2 md:top-1/2 md:max-h-[90vh] md:-translate-x-1/2 md:-translate-y-1/2"
            )}
          >
            {/* Close Button */}
            <button
              onClick={onClose}
              className={cn(
                "absolute top-4 z-10 flex h-10 w-10 items-center justify-center rounded-full",
                "bg-white/90 text-gray-600 shadow-md backdrop-blur-sm",
                "transition-all hover:bg-white hover:shadow-lg",
                isRTL ? "left-4" : "right-4"
              )}
            >
              <X className="h-5 w-5" />
            </button>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto">
              {/* Image */}
              {item.image ? (
                <div className="relative aspect-video w-full">
                  <Image
                    src={item.image}
                    alt={displayName}
                    fill
                    className="object-cover"
                  />
                  {/* Gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-white/20 to-transparent" />
                </div>
              ) : (
                <div className="flex aspect-video w-full items-center justify-center bg-gray-100 text-7xl">
                  <span role="img" aria-label="food">&#127869;</span>
                </div>
              )}

              {/* Content */}
              <div className="p-6 space-y-6">
                {/* Header */}
                <div>
                  <h2 className="mb-2 text-2xl font-bold text-gray-900">{displayName}</h2>
                  {displayDescription && (
                    <p className="text-gray-500">{displayDescription}</p>
                  )}
                  <p className="mt-2 text-xl font-bold text-emerald-600">
                    {formatPrice(basePrice)}
                  </p>
                </div>

                {/* Variants (Radio Buttons) */}
                {item.variants && item.variants.length > 0 && (
                  <div>
                    <h3 className="mb-3 font-semibold text-gray-900">
                      {t("selectSize")} <span className="text-[#f43f5e]">*</span>
                    </h3>
                    <div className="space-y-2">
                      {item.variants.map((variant) => {
                        const variantNameAr = variant.nameAr || variant.name_ar;
                        const variantName =
                          locale === "ar" && variantNameAr
                            ? variantNameAr
                            : variant.name;
                        const isSelected = String(selectedVariant?.id) === String(variant.id);

                        return (
                          <button
                            key={variant.id}
                            onClick={() => setSelectedVariant(variant)}
                            className={cn(
                              "flex w-full items-center justify-between rounded-xl border-2 p-4 transition-all",
                              isSelected
                                ? "border-emerald-500 bg-emerald-50"
                                : "border-gray-200 hover:border-emerald-300 hover:bg-gray-50"
                            )}
                          >
                            <div className="flex items-center gap-3">
                              {/* Radio Button */}
                              <div
                                className={cn(
                                  "flex h-5 w-5 items-center justify-center rounded-full border-2 transition-all",
                                  isSelected
                                    ? "border-emerald-500 bg-emerald-500"
                                    : "border-gray-300"
                                )}
                              >
                                {isSelected && (
                                  <div className="h-2 w-2 rounded-full bg-white" />
                                )}
                              </div>
                              <span className={cn(
                                "font-medium",
                                isSelected ? "text-gray-900" : "text-gray-700"
                              )}>
                                {variantName}
                              </span>
                            </div>
                            <span className="font-semibold text-emerald-600">
                              {formatPrice(variant.price)}
                            </span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Addons (Checkboxes) */}
                {item.addons && item.addons.length > 0 && (
                  <div>
                    <h3 className="mb-3 font-semibold text-gray-900">{t("selectOptions")}</h3>
                    <div className="space-y-2">
                      {item.addons.map((addon) => {
                        const addonNameAr = addon.nameAr || addon.name_ar;
                        const addonName =
                          locale === "ar" && addonNameAr
                            ? addonNameAr
                            : addon.name;
                        const isSelected = selectedAddons.has(String(addon.id));

                        return (
                          <button
                            key={addon.id}
                            onClick={() => toggleAddon(addon)}
                            className={cn(
                              "flex w-full items-center justify-between rounded-xl border-2 p-4 transition-all",
                              isSelected
                                ? "border-emerald-500 bg-emerald-50"
                                : "border-gray-200 hover:border-emerald-300 hover:bg-gray-50"
                            )}
                          >
                            <div className="flex items-center gap-3">
                              {/* Checkbox */}
                              <div
                                className={cn(
                                  "flex h-5 w-5 items-center justify-center rounded border-2 transition-all",
                                  isSelected
                                    ? "border-emerald-500 bg-emerald-500"
                                    : "border-gray-300"
                                )}
                              >
                                {isSelected && (
                                  <Check className="h-3 w-3 text-white" />
                                )}
                              </div>
                              <span className={cn(
                                "font-medium",
                                isSelected ? "text-gray-900" : "text-gray-700"
                              )}>
                                {addonName}
                              </span>
                            </div>
                            <span className="text-sm font-medium text-emerald-600">
                              +{formatPrice(addon.price)}
                            </span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Special Instructions */}
                <div>
                  <h3 className="mb-3 font-semibold text-gray-900">{t("specialInstructions")}</h3>
                  <Textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder={t("specialInstructionsPlaceholder")}
                    rows={2}
                    className={cn(
                      "rounded-xl border-gray-200 bg-gray-50",
                      "focus:border-emerald-500 focus:ring-emerald-500/20",
                      "placeholder:text-gray-400"
                    )}
                  />
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-gray-100 bg-white p-4 shadow-lg shadow-gray-200/50">
              {/* Quantity */}
              <div className="mb-4 flex items-center justify-between">
                <span className="font-medium text-gray-700">{t("quantity")}</span>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    disabled={quantity <= 1}
                    className={cn(
                      "flex h-10 w-10 items-center justify-center rounded-full",
                      "border-2 border-gray-200 text-gray-600",
                      "transition-all hover:border-emerald-500 hover:text-emerald-600",
                      "disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-gray-200 disabled:hover:text-gray-600"
                    )}
                  >
                    <Minus className="h-4 w-4" />
                  </button>
                  <span className="w-8 text-center text-lg font-bold text-gray-900">
                    {quantity}
                  </span>
                  <button
                    onClick={() => setQuantity(quantity + 1)}
                    className={cn(
                      "flex h-10 w-10 items-center justify-center rounded-full",
                      "bg-emerald-500 text-white",
                      "transition-all hover:bg-emerald-600",
                      "shadow-md shadow-emerald-500/30"
                    )}
                  >
                    <Plus className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Add to Cart Button */}
              <Button
                onClick={handleAddToCart}
                className={cn(
                  "w-full h-14 text-base font-semibold rounded-xl",
                  "bg-emerald-500 hover:bg-emerald-600",
                  "shadow-lg shadow-emerald-500/30",
                  "transition-all hover:shadow-xl hover:shadow-emerald-500/40"
                )}
                size="lg"
                disabled={!isAvailable || (item.variants && item.variants.length > 0 && !selectedVariant)}
              >
                {!isAvailable ? (
                  isRTL ? "غير متوفر" : "Unavailable"
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <ShoppingCart className="h-5 w-5" />
                    {t("addToCart")} - {formatPrice(itemTotal)}
                  </span>
                )}
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
