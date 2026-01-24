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
  MessageCircle,
  ShoppingBag,
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
  const isRTL = locale === "ar";

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

  // Step indicators
  const steps = [
    { number: 1, label: isRTL ? "معلومات التوصيل" : "Delivery Info", icon: MapPin },
    { number: 2, label: isRTL ? "وقت التوصيل" : "Delivery Time", icon: ShoppingBag },
    { number: 3, label: isRTL ? "طريقة الدفع" : "Payment", icon: CreditCard },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Back Button */}
        <Link
          href={`/${locale}/cart`}
          className="mb-6 inline-flex items-center gap-1 text-sm text-gray-500 transition-colors hover:text-emerald-600"
        >
          {isRTL ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
          {isRTL ? "العودة للسلة" : "Back to cart"}
        </Link>

        {/* Page Title */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 md:text-3xl">
            {t("title")}
          </h1>
          <p className="mt-1 text-gray-500">
            {isRTL ? "اكمل طلبك بملء المعلومات المطلوبة" : "Complete your order by filling in the required information"}
          </p>
        </div>

        {/* Step Indicators */}
        <div className="mb-8 hidden md:block">
          <div className="flex items-center justify-center gap-4">
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500 text-sm font-medium text-white">
                    {step.number}
                  </div>
                  <span className="text-sm font-medium text-gray-700">{step.label}</span>
                </div>
                {index < steps.length - 1 && (
                  <div className={cn(
                    "mx-4 h-0.5 w-12 bg-emerald-200",
                    isRTL && "rotate-180"
                  )} />
                )}
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-8 lg:grid-cols-3">
            {/* Form Fields */}
            <div className="space-y-6 lg:col-span-2">
              {/* Delivery Info */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-2xl bg-white p-6 shadow-sm"
              >
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100">
                    <MapPin className="h-5 w-5 text-emerald-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">
                      {t("deliveryInfo.title")}
                    </h2>
                    <p className="text-sm text-gray-500">
                      {isRTL ? "أين نوصل طلبك؟" : "Where should we deliver?"}
                    </p>
                  </div>
                </div>

                <div className="space-y-4">
                  {/* Name */}
                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                      {t("deliveryInfo.name")} <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <User className={cn(
                        "absolute top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400",
                        isRTL ? "right-4" : "left-4"
                      )} />
                      <Input
                        value={formData.name}
                        onChange={(e) => handleInputChange("name", e.target.value)}
                        placeholder={t("deliveryInfo.namePlaceholder")}
                        className={cn(
                          "h-12 border-gray-200 bg-gray-50 focus:border-emerald-500 focus:bg-white focus:ring-emerald-500",
                          isRTL ? "pr-12" : "pl-12",
                          errors.name && "border-red-500 focus:border-red-500 focus:ring-red-500"
                        )}
                      />
                    </div>
                    {errors.name && (
                      <p className="mt-1 text-sm text-red-500">{errors.name}</p>
                    )}
                  </div>

                  {/* Phone */}
                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                      {t("deliveryInfo.phone")} <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <Phone className={cn(
                        "absolute top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400",
                        isRTL ? "right-4" : "left-4"
                      )} />
                      <Input
                        value={formData.phone}
                        onChange={(e) => handleInputChange("phone", e.target.value)}
                        placeholder={t("deliveryInfo.phonePlaceholder")}
                        className={cn(
                          "h-12 border-gray-200 bg-gray-50 focus:border-emerald-500 focus:bg-white focus:ring-emerald-500",
                          isRTL ? "pr-12" : "pl-12",
                          errors.phone && "border-red-500 focus:border-red-500 focus:ring-red-500"
                        )}
                        type="tel"
                        dir="ltr"
                      />
                    </div>
                    {errors.phone && (
                      <p className="mt-1 text-sm text-red-500">{errors.phone}</p>
                    )}
                  </div>

                  {/* Address */}
                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                      {t("deliveryInfo.address")} <span className="text-red-500">*</span>
                    </label>
                    <Textarea
                      value={formData.address}
                      onChange={(e) => handleInputChange("address", e.target.value)}
                      placeholder={t("deliveryInfo.addressPlaceholder")}
                      rows={3}
                      className={cn(
                        "border-gray-200 bg-gray-50 focus:border-emerald-500 focus:bg-white focus:ring-emerald-500",
                        errors.address && "border-red-500 focus:border-red-500 focus:ring-red-500"
                      )}
                    />
                    {errors.address && (
                      <p className="mt-1 text-sm text-red-500">{errors.address}</p>
                    )}
                  </div>
                </div>
              </motion.div>

              {/* Delivery Time (Scheduling) */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="rounded-2xl bg-white p-6 shadow-sm"
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
                className="rounded-2xl bg-white p-6 shadow-sm"
              >
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100">
                    <CreditCard className="h-5 w-5 text-emerald-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">
                      {t("payment.title")}
                    </h2>
                    <p className="text-sm text-gray-500">
                      {isRTL ? "كيف تريد الدفع؟" : "How would you like to pay?"}
                    </p>
                  </div>
                </div>

                <div className="space-y-3">
                  {/* Cash */}
                  <button
                    type="button"
                    onClick={() => setPaymentMethod("cash")}
                    className={cn(
                      "flex w-full items-center gap-4 rounded-xl border-2 p-4 transition-all",
                      paymentMethod === "cash"
                        ? "border-emerald-500 bg-emerald-50"
                        : "border-gray-200 bg-white hover:border-emerald-300 hover:bg-gray-50"
                    )}
                  >
                    <div
                      className={cn(
                        "flex h-12 w-12 items-center justify-center rounded-full",
                        paymentMethod === "cash"
                          ? "bg-emerald-500 text-white"
                          : "bg-gray-100 text-gray-500"
                      )}
                    >
                      <Wallet className="h-6 w-6" />
                    </div>
                    <div className="flex-1 text-start">
                      <p className={cn(
                        "font-medium",
                        paymentMethod === "cash" ? "text-emerald-700" : "text-gray-900"
                      )}>
                        {t("payment.cash")}
                      </p>
                      <p className="text-sm text-gray-500">
                        {isRTL ? "ادفع عند الاستلام" : "Pay when you receive your order"}
                      </p>
                    </div>
                    {paymentMethod === "cash" && (
                      <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500">
                        <Check className="h-4 w-4 text-white" />
                      </div>
                    )}
                  </button>

                  {/* Card (Coming Soon) */}
                  <div
                    className="flex w-full cursor-not-allowed items-center gap-4 rounded-xl border-2 border-gray-200 bg-gray-50 p-4 opacity-60"
                  >
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-200 text-gray-400">
                      <CreditCard className="h-6 w-6" />
                    </div>
                    <div className="flex-1 text-start">
                      <p className="font-medium text-gray-500">{t("payment.card")}</p>
                      <p className="text-sm text-gray-400">
                        {t("payment.cardComingSoon")}
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* WhatsApp Info Section */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6"
              >
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-emerald-500">
                    <MessageCircle className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-emerald-800">
                      {isRTL ? "تتبع طلبك عبر واتساب" : "Track Your Order via WhatsApp"}
                    </h3>
                    <p className="mt-1 text-sm text-emerald-700">
                      {isRTL
                        ? "سنرسل لك تحديثات عن حالة طلبك مباشرة على رقم الهاتف الذي أدخلته."
                        : "We'll send you order status updates directly to the phone number you provided."}
                    </p>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 }}
                className="sticky top-24 rounded-2xl bg-white p-6 shadow-sm"
              >
                <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-gray-900">
                  <ShoppingBag className="h-5 w-5 text-emerald-600" />
                  {t("summary.title")}
                </h2>

                {/* Restaurant */}
                {displayRestaurantName && (
                  <div className="mb-4 rounded-xl bg-gray-50 p-3">
                    <p className="text-xs text-gray-500">
                      {isRTL ? "من:" : "From:"}
                    </p>
                    <p className="font-medium text-gray-900">{displayRestaurantName}</p>
                  </div>
                )}

                {/* Items */}
                <div className="mb-4 max-h-48 space-y-2 overflow-y-auto">
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
                        <span className="text-gray-600">
                          <span className="inline-flex h-5 w-5 items-center justify-center rounded bg-emerald-100 text-xs font-medium text-emerald-700">
                            {item.quantity}
                          </span>
                          <span className={cn("mx-1", isRTL ? "mr-2" : "ml-2")}>{displayName}</span>
                        </span>
                        <span className="font-medium text-gray-900">{formatPrice(itemPrice * item.quantity)}</span>
                      </div>
                    );
                  })}
                </div>

                {/* Totals */}
                <div className="space-y-3 border-t border-gray-100 pt-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">
                      {isRTL ? "المجموع الفرعي" : "Subtotal"}
                    </span>
                    <span className="text-gray-900">{formatPrice(getSubtotal())}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">
                      {isRTL ? "التوصيل" : "Delivery"}
                    </span>
                    <span className="text-gray-900">{formatPrice(getDeliveryFee())}</span>
                  </div>
                  <div className="flex justify-between border-t border-gray-100 pt-3 text-base">
                    <span className="font-semibold text-gray-900">{isRTL ? "المجموع" : "Total"}</span>
                    <span className="font-bold text-emerald-600">{formatPrice(getTotal())}</span>
                  </div>
                </div>

                {/* Error Message */}
                {submitError && (
                  <div className="mt-4 flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-600">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    <span>{submitError}</span>
                  </div>
                )}

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="mt-6 h-14 w-full bg-emerald-500 text-base font-semibold text-white shadow-lg shadow-emerald-500/30 transition-all hover:bg-emerald-600 hover:shadow-xl hover:shadow-emerald-500/40"
                  size="lg"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className={cn("h-5 w-5 animate-spin", isRTL ? "ml-2" : "mr-2")} />
                      {t("processing")}
                    </>
                  ) : (
                    <>
                      <Check className={cn("h-5 w-5", isRTL ? "ml-2" : "mr-2")} />
                      {t("placeOrder")}
                      <span className="mx-2">-</span>
                      {formatPrice(getTotal())}
                    </>
                  )}
                </Button>

                {/* Security Note */}
                <p className="mt-4 text-center text-xs text-gray-400">
                  {isRTL
                    ? "معلوماتك محمية ومشفرة"
                    : "Your information is protected and encrypted"}
                </p>
              </motion.div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
