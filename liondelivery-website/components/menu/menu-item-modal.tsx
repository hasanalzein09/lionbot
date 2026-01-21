"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { useLocale, useTranslations } from "next-intl";
import { motion, AnimatePresence } from "framer-motion";
import { X, Minus, Plus, Check } from "lucide-react";
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

  const displayName = locale === "ar" && item.nameAr ? item.nameAr : item.name;
  const displayDescription =
    locale === "ar" && item.descriptionAr ? item.descriptionAr : item.description;

  // Calculate total price
  const basePrice = selectedVariant?.price || item.price;
  const addonsTotal = Array.from(selectedAddons.entries()).reduce(
    (total, [addonId, qty]) => {
      const addon = item.addons?.find((a) => a.id === addonId);
      return total + (addon?.price || 0) * qty;
    },
    0
  );
  const itemTotal = (basePrice + addonsTotal) * quantity;

  const toggleAddon = (addon: MenuItemAddon) => {
    const newAddons = new Map(selectedAddons);
    if (newAddons.has(addon.id)) {
      newAddons.delete(addon.id);
    } else {
      newAddons.set(addon.id, 1);
    }
    setSelectedAddons(newAddons);
  };

  const handleAddToCart = () => {
    const cartAddons = item.addons
      ?.filter((addon) => selectedAddons.has(addon.id))
      .map((addon) => ({
        id: addon.id,
        name: addon.name,
        nameAr: addon.nameAr,
        price: addon.price,
        quantity: selectedAddons.get(addon.id) || 1,
      }));

    addItem({
      productId: item.id,
      name: item.name,
      nameAr: item.nameAr,
      description: item.description,
      image: item.image,
      price: item.price,
      quantity,
      variant: selectedVariant
        ? {
            id: selectedVariant.id,
            name: selectedVariant.name,
            nameAr: selectedVariant.nameAr,
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
            className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-x-4 bottom-4 top-4 z-50 mx-auto flex max-w-lg flex-col overflow-hidden rounded-3xl bg-secondary-900 shadow-2xl md:inset-auto md:left-1/2 md:top-1/2 md:max-h-[90vh] md:-translate-x-1/2 md:-translate-y-1/2"
          >
            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute right-4 top-4 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-black/50 text-white backdrop-blur-sm transition-colors hover:bg-black/70"
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
                </div>
              ) : (
                <div className="flex aspect-video w-full items-center justify-center bg-secondary-800 text-7xl">
                  🍽️
                </div>
              )}

              {/* Content */}
              <div className="p-6 space-y-6">
                {/* Header */}
                <div>
                  <h2 className="mb-2 text-2xl font-bold">{displayName}</h2>
                  {displayDescription && (
                    <p className="text-muted-foreground">{displayDescription}</p>
                  )}
                </div>

                {/* Variants */}
                {item.variants && item.variants.length > 0 && (
                  <div>
                    <h3 className="mb-3 font-semibold">
                      {t("selectSize")} <span className="text-error-500">*</span>
                    </h3>
                    <div className="space-y-2">
                      {item.variants.map((variant) => {
                        const variantName =
                          locale === "ar" && variant.nameAr
                            ? variant.nameAr
                            : variant.name;
                        const isSelected = selectedVariant?.id === variant.id;

                        return (
                          <button
                            key={variant.id}
                            onClick={() => setSelectedVariant(variant)}
                            className={cn(
                              "flex w-full items-center justify-between rounded-xl border-2 p-4 transition-all",
                              isSelected
                                ? "border-primary-500 bg-primary-500/10"
                                : "border-border hover:border-primary-500/50"
                            )}
                          >
                            <div className="flex items-center gap-3">
                              <div
                                className={cn(
                                  "flex h-5 w-5 items-center justify-center rounded-full border-2",
                                  isSelected
                                    ? "border-primary-500 bg-primary-500"
                                    : "border-muted-foreground"
                                )}
                              >
                                {isSelected && (
                                  <Check className="h-3 w-3 text-white" />
                                )}
                              </div>
                              <span className="font-medium">{variantName}</span>
                            </div>
                            <span className="font-semibold text-primary-500">
                              {formatPrice(variant.price)}
                            </span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Addons */}
                {item.addons && item.addons.length > 0 && (
                  <div>
                    <h3 className="mb-3 font-semibold">{t("selectOptions")}</h3>
                    <div className="space-y-2">
                      {item.addons.map((addon) => {
                        const addonName =
                          locale === "ar" && addon.nameAr
                            ? addon.nameAr
                            : addon.name;
                        const isSelected = selectedAddons.has(addon.id);

                        return (
                          <button
                            key={addon.id}
                            onClick={() => toggleAddon(addon)}
                            className={cn(
                              "flex w-full items-center justify-between rounded-xl border-2 p-4 transition-all",
                              isSelected
                                ? "border-primary-500 bg-primary-500/10"
                                : "border-border hover:border-primary-500/50"
                            )}
                          >
                            <div className="flex items-center gap-3">
                              <div
                                className={cn(
                                  "flex h-5 w-5 items-center justify-center rounded border-2",
                                  isSelected
                                    ? "border-primary-500 bg-primary-500"
                                    : "border-muted-foreground"
                                )}
                              >
                                {isSelected && (
                                  <Check className="h-3 w-3 text-white" />
                                )}
                              </div>
                              <span className="font-medium">{addonName}</span>
                            </div>
                            <span className="text-sm text-primary-500">
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
                  <h3 className="mb-3 font-semibold">{t("specialInstructions")}</h3>
                  <Textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder={t("specialInstructionsPlaceholder")}
                    rows={2}
                  />
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="border-t border-border bg-secondary-800/50 p-4">
              {/* Quantity */}
              <div className="mb-4 flex items-center justify-between">
                <span className="font-medium">{t("quantity")}</span>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    disabled={quantity <= 1}
                    className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-700 text-foreground transition-colors hover:bg-secondary-600 disabled:opacity-50"
                  >
                    <Minus className="h-4 w-4" />
                  </button>
                  <span className="w-8 text-center text-lg font-semibold">
                    {quantity}
                  </span>
                  <button
                    onClick={() => setQuantity(quantity + 1)}
                    className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-500 text-white transition-colors hover:bg-primary-600"
                  >
                    <Plus className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Add to Cart Button */}
              <Button
                onClick={handleAddToCart}
                className="w-full"
                size="lg"
                disabled={item.variants && item.variants.length > 0 && !selectedVariant}
              >
                {t("addToCart")} • {formatPrice(itemTotal)}
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
