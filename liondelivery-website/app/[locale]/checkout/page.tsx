"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import {
  ChevronLeft,
  ChevronRight,
  User,
  Phone,
  MapPin,
  CreditCard,
  Wallet,
  Loader2,
  Check,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { DeliveryTimeSelector } from "@/components/checkout/delivery-time-selector";
import { useCartStore } from "@/lib/stores/cart-store";
import { ordersApi } from "@/lib/api/orders";
import { formatPrice } from "@/lib/utils/formatters";
import { cn } from "@/lib/utils/cn";

type PaymentMethod = "cash" | "card";

interface FormData {
  name: string;
  phone: string;
  address: string;
}

interface FormErrors {
  name?: string;
  phone?: string;
  address?: string;
}

export default function CheckoutPage() {
  const locale = useLocale();
  const t = useTranslations("checkout");
  const router = useRouter();

  const {
    items,
    restaurantId,
    restaurantName,
    restaurantNameAr,
    notes,
    getSubtotal,
    getDeliveryFee,
    getTotal,
    clearCart,
  } = useCartStore();

  const [formData, setFormData] = useState<FormData>({
    name: "",
    phone: "",
    address: "",
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("cash");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [scheduledTime, setScheduledTime] = useState<string | null>(null);

  const displayRestaurantName =
    locale === "ar" && restaurantNameAr ? restaurantNameAr : restaurantName;

  // Redirect if cart is empty
  if (items.length === 0) {
    router.push(`/${locale}/cart`);
    return null;
  }

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = t("errors.nameRequired");
    }

    if (!formData.phone.trim()) {
      newErrors.phone = t("errors.phoneRequired");
    } else if (!/^(\+?961|0)?[0-9]{7,8}$/.test(formData.phone.replace(/\s/g, ""))) {
      newErrors.phone = t("errors.phoneInvalid");
    }

    if (!formData.address.trim()) {
      newErrors.address = t("errors.addressRequired");
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    if (!restaurantId) {
      setSubmitError(locale === "ar" ? "خطأ في السلة" : "Cart error");
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // Prepare order items for API
      const orderItems = items.map((item) => ({
        product_id: parseInt(item.productId),
        name: item.name,
        name_ar: item.nameAr || null,
        price: item.variant?.price || item.price,
        quantity: item.quantity,
        variant_id: item.variant?.id ? parseInt(item.variant.id) : null,
        variant_name: item.variant?.name || null,
        variant_price: item.variant?.price || null,
        notes: item.notes || null,
      }));

      // Call the real orders API
      const response = await ordersApi.create({
        restaurant_id: parseInt(restaurantId),
        items: orderItems,
        customer: formData,
        notes: notes || null,
        payment_method: paymentMethod,
        scheduled_time: scheduledTime,
      });

      if (response.success) {
        // Clear cart
        clearCart();

        // Redirect to order confirmation
        router.push(`/${locale}/orders/${response.order.order_number}`);
      } else {
        setSubmitError(response.message || (locale === "ar" ? "فشل في إرسال الطلب" : "Failed to place order"));
        setIsSubmitting(false);
      }
    } catch (error) {
      console.error("Order submission failed:", error);
      setSubmitError(locale === "ar" ? "حدث خطأ، الرجاء المحاولة مرة أخرى" : "An error occurred, please try again");
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4">
        {/* Back Button */}
        <Link
          href={`/${locale}/cart`}
          className="mb-6 inline-flex items-center text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          {locale === "ar" ? (
            <ChevronRight className="mr-1 h-4 w-4" />
          ) : (
            <ChevronLeft className="mr-1 h-4 w-4" />
          )}
          {locale === "ar" ? "العودة للسلة" : "Back to cart"}
        </Link>

        <h1 className="mb-8 text-2xl font-bold md:text-3xl">
          📦 {t("title")}
        </h1>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-8 lg:grid-cols-3">
            {/* Form Fields */}
            <div className="space-y-6 lg:col-span-2">
              {/* Delivery Info */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-2xl bg-secondary-800 p-6"
              >
                <h2 className="mb-6 flex items-center gap-2 text-lg font-semibold">
                  <MapPin className="h-5 w-5 text-primary-500" />
                  {t("deliveryInfo.title")}
                </h2>

                <div className="space-y-4">
                  {/* Name */}
                  <div>
                    <label className="mb-2 block text-sm font-medium">
                      {t("deliveryInfo.name")} <span className="text-error-500">*</span>
                    </label>
                    <div className="relative">
                      <User className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        value={formData.name}
                        onChange={(e) => handleInputChange("name", e.target.value)}
                        placeholder={t("deliveryInfo.namePlaceholder")}
                        className="pl-12"
                        error={!!errors.name}
                      />
                    </div>
                    {errors.name && (
                      <p className="mt-1 text-sm text-error-500">{errors.name}</p>
                    )}
                  </div>

                  {/* Phone */}
                  <div>
                    <label className="mb-2 block text-sm font-medium">
                      {t("deliveryInfo.phone")} <span className="text-error-500">*</span>
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        value={formData.phone}
                        onChange={(e) => handleInputChange("phone", e.target.value)}
                        placeholder={t("deliveryInfo.phonePlaceholder")}
                        className="pl-12"
                        type="tel"
                        dir="ltr"
                        error={!!errors.phone}
                      />
                    </div>
                    {errors.phone && (
                      <p className="mt-1 text-sm text-error-500">{errors.phone}</p>
                    )}
                  </div>

                  {/* Address */}
                  <div>
                    <label className="mb-2 block text-sm font-medium">
                      {t("deliveryInfo.address")} <span className="text-error-500">*</span>
                    </label>
                    <Textarea
                      value={formData.address}
                      onChange={(e) => handleInputChange("address", e.target.value)}
                      placeholder={t("deliveryInfo.addressPlaceholder")}
                      rows={3}
                      error={!!errors.address}
                    />
                    {errors.address && (
                      <p className="mt-1 text-sm text-error-500">{errors.address}</p>
                    )}
                  </div>
                </div>
              </motion.div>

              {/* Delivery Time (Scheduling) */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="rounded-2xl bg-secondary-800 p-6"
              >
                {restaurantId && (
                  <DeliveryTimeSelector
                    restaurantId={parseInt(restaurantId)}
                    onSelect={setScheduledTime}
                    selectedTime={scheduledTime}
                  />
                )}
              </motion.div>

              {/* Payment Method */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
                className="rounded-2xl bg-secondary-800 p-6"
              >
                <h2 className="mb-6 flex items-center gap-2 text-lg font-semibold">
                  <CreditCard className="h-5 w-5 text-primary-500" />
                  {t("payment.title")}
                </h2>

                <div className="space-y-3">
                  {/* Cash */}
                  <button
                    type="button"
                    onClick={() => setPaymentMethod("cash")}
                    className={cn(
                      "flex w-full items-center gap-4 rounded-xl border-2 p-4 transition-all",
                      paymentMethod === "cash"
                        ? "border-primary-500 bg-primary-500/10"
                        : "border-border hover:border-primary-500/50"
                    )}
                  >
                    <div
                      className={cn(
                        "flex h-10 w-10 items-center justify-center rounded-full",
                        paymentMethod === "cash"
                          ? "bg-primary-500 text-white"
                          : "bg-secondary-700 text-muted-foreground"
                      )}
                    >
                      <Wallet className="h-5 w-5" />
                    </div>
                    <div className="flex-1 text-start">
                      <p className="font-medium">{t("payment.cash")}</p>
                    </div>
                    {paymentMethod === "cash" && (
                      <Check className="h-5 w-5 text-primary-500" />
                    )}
                  </button>

                  {/* Card (Coming Soon) */}
                  <div
                    className="flex w-full cursor-not-allowed items-center gap-4 rounded-xl border-2 border-border bg-secondary-700/50 p-4 opacity-50"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-700 text-muted-foreground">
                      <CreditCard className="h-5 w-5" />
                    </div>
                    <div className="flex-1 text-start">
                      <p className="font-medium">{t("payment.card")}</p>
                      <p className="text-xs text-muted-foreground">
                        {t("payment.cardComingSoon")}
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="sticky top-24 rounded-2xl bg-secondary-800 p-6"
              >
                <h2 className="mb-4 text-lg font-semibold">{t("summary.title")}</h2>

                {/* Restaurant */}
                {displayRestaurantName && (
                  <div className="mb-4 rounded-xl bg-secondary-700/50 p-3">
                    <p className="text-sm text-muted-foreground">
                      {locale === "ar" ? "من:" : "From:"}
                    </p>
                    <p className="font-medium">{displayRestaurantName}</p>
                  </div>
                )}

                {/* Items */}
                <div className="mb-4 space-y-2">
                  {items.map((item) => {
                    const displayName =
                      locale === "ar" && item.nameAr ? item.nameAr : item.name;
                    let itemPrice = item.variant?.price || item.price;
                    if (item.addons) {
                      itemPrice += item.addons.reduce(
                        (sum, addon) => sum + addon.price * addon.quantity,
                        0
                      );
                    }

                    return (
                      <div key={item.id} className="flex justify-between text-sm">
                        <span className="text-muted-foreground">
                          {item.quantity}x {displayName}
                        </span>
                        <span>{formatPrice(itemPrice * item.quantity)}</span>
                      </div>
                    );
                  })}
                </div>

                {/* Totals */}
                <div className="space-y-2 border-t border-border pt-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">
                      {locale === "ar" ? "المجموع الفرعي" : "Subtotal"}
                    </span>
                    <span>{formatPrice(getSubtotal())}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">
                      {locale === "ar" ? "التوصيل" : "Delivery"}
                    </span>
                    <span>{formatPrice(getDeliveryFee())}</span>
                  </div>
                  <div className="flex justify-between border-t border-border pt-2 text-base font-semibold">
                    <span>{locale === "ar" ? "المجموع" : "Total"}</span>
                    <span className="text-primary-500">{formatPrice(getTotal())}</span>
                  </div>
                </div>

                {/* Error Message */}
                {submitError && (
                  <div className="mt-4 flex items-center gap-2 rounded-lg bg-error-500/10 p-3 text-sm text-error-500">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    <span>{submitError}</span>
                  </div>
                )}

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="mt-6 w-full"
                  size="lg"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {t("processing")}
                    </>
                  ) : (
                    <>
                      {t("placeOrder")}
                      <span className="mx-2">•</span>
                      {formatPrice(getTotal())}
                    </>
                  )}
                </Button>
              </motion.div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
