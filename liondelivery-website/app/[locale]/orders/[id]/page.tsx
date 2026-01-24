"use client";

import { use } from "react";
import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import {
  CheckCircle,
  Clock,
  MapPin,
  Phone,
  MessageCircle,
  Home,
  Package,
  ChefHat,
  Truck,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { SITE_CONFIG } from "@/lib/utils/constants";
import { ordersApi, type Order, type OrderStatus } from "@/lib/api/orders";
import { formatPrice } from "@/lib/utils/formatters";

interface OrderPageProps {
  params: Promise<{ locale: string; id: string }>;
}

// Map API status to display
const statusConfig: Record<OrderStatus, { step: number; labelKey: string }> = {
  new: { step: 1, labelKey: "confirmed" },
  accepted: { step: 1, labelKey: "confirmed" },
  preparing: { step: 2, labelKey: "preparing" },
  ready: { step: 3, labelKey: "ready" },
  out_for_delivery: { step: 4, labelKey: "delivering" },
  delivered: { step: 5, labelKey: "delivered" },
  cancelled: { step: 0, labelKey: "cancelled" },
};

export default function OrderPage({ params }: OrderPageProps) {
  const { locale, id: orderId } = use(params);
  const t = useTranslations("order");

  // Fetch order data from API
  const { data: order, isLoading, error } = useQuery({
    queryKey: ["order", orderId],
    queryFn: () => ordersApi.getByNumber(orderId),
    retry: 1,
  });

  const currentStep = order ? (statusConfig[order.status]?.step || 1) : 1;

  const orderStatuses = [
    {
      id: "confirmed",
      step: 1,
      label: t("status.confirmed"),
      icon: CheckCircle,
    },
    {
      id: "preparing",
      step: 2,
      label: t("status.preparing"),
      icon: ChefHat,
    },
    {
      id: "ready",
      step: 3,
      label: t("status.ready"),
      icon: Package,
    },
    {
      id: "delivering",
      step: 4,
      label: t("status.delivering"),
      icon: Truck,
    },
  ];

  const whatsappUrl = `https://wa.me/${SITE_CONFIG.contact.whatsapp.replace(/[^0-9]/g, "")}?text=${encodeURIComponent(
    locale === "ar"
      ? `مرحباً، أريد الاستفسار عن طلبي رقم ${orderId}`
      : `Hello, I want to inquire about my order ${orderId}`
  )}`;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background py-12">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-2xl space-y-6">
            <div className="text-center">
              <Skeleton className="mx-auto h-24 w-24 rounded-full" />
              <Skeleton className="mx-auto mt-6 h-8 w-48" />
              <Skeleton className="mx-auto mt-2 h-5 w-32" />
            </div>
            <Skeleton className="h-64 w-full rounded-2xl" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background py-12">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-2xl text-center">
            <AlertCircle className="mx-auto h-16 w-16 text-error-500" />
            <h1 className="mt-4 text-2xl font-bold">
              {locale === "ar" ? "الطلب غير موجود" : "Order not found"}
            </h1>
            <p className="mt-2 text-muted-foreground">
              {locale === "ar"
                ? "لم نتمكن من العثور على هذا الطلب"
                : "We couldn't find this order"}
            </p>
            <Link href={`/${locale}`} className="mt-6 inline-block">
              <Button>
                <Home className="mr-2 h-5 w-5" />
                {locale === "ar" ? "العودة للرئيسية" : "Back to Home"}
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mx-auto max-w-2xl"
        >
          {/* Success Header */}
          <div className="mb-8 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", damping: 10, delay: 0.2 }}
              className="mb-6 inline-flex h-24 w-24 items-center justify-center rounded-full bg-success-500/20"
            >
              <CheckCircle className="h-12 w-12 text-success-500" />
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mb-2 text-2xl font-bold md:text-3xl"
            >
              {t("success.title")}
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-muted-foreground"
            >
              {t("success.orderNumber")}:{" "}
              <span className="font-mono font-semibold text-primary-500">
                #{order?.order_number || orderId}
              </span>
            </motion.p>
          </div>

          {/* Order Details */}
          {order && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.45 }}
              className="mb-6 rounded-2xl bg-secondary-800 p-6"
            >
              <h2 className="mb-4 font-semibold">
                {locale === "ar" ? "تفاصيل الطلب" : "Order Details"}
              </h2>

              {/* Restaurant */}
              {order.restaurant && (
                <div className="mb-4 rounded-xl bg-secondary-700/50 p-3">
                  <p className="text-sm text-muted-foreground">
                    {locale === "ar" ? "من:" : "From:"}
                  </p>
                  <p className="font-medium">
                    {locale === "ar" && order.restaurant.name_ar
                      ? order.restaurant.name_ar
                      : order.restaurant.name}
                  </p>
                </div>
              )}

              {/* Items */}
              <div className="space-y-2">
                {order.items.map((item) => (
                  <div key={item.id} className="flex justify-between text-sm">
                    <span className="text-muted-foreground">
                      {item.quantity}x{" "}
                      {locale === "ar" && item.name_ar ? item.name_ar : item.name}
                    </span>
                    <span>{formatPrice(item.total_price)}</span>
                  </div>
                ))}
              </div>

              {/* Totals */}
              <div className="mt-4 space-y-2 border-t border-border pt-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    {locale === "ar" ? "التوصيل" : "Delivery"}
                  </span>
                  <span>{formatPrice(order.delivery_fee)}</span>
                </div>
                <div className="flex justify-between font-semibold">
                  <span>{locale === "ar" ? "المجموع" : "Total"}</span>
                  <span className="text-primary-500">{formatPrice(order.total)}</span>
                </div>
              </div>
            </motion.div>
          )}

          {/* Order Status Timeline */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mb-8 rounded-2xl bg-secondary-800 p-6"
          >
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-semibold">
                {locale === "ar" ? "حالة الطلب" : "Order Status"}
              </h2>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span>
                  {t("success.estimatedTime")}: 25-35 {t("success.minutes")}
                </span>
              </div>
            </div>

            {/* Timeline */}
            <div className="relative">
              <div className="absolute left-5 top-0 h-full w-0.5 bg-border" />
              <div className="space-y-6">
                {orderStatuses.map((status) => {
                  const Icon = status.icon;
                  const isCompleted = status.step < currentStep;
                  const isActive = status.step === currentStep;

                  return (
                    <div key={status.id} className="relative flex items-center gap-4">
                      <div
                        className={`relative z-10 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full ${
                          isCompleted
                            ? "bg-success-500 text-white"
                            : isActive
                            ? "bg-primary-500 text-white"
                            : "bg-secondary-700 text-muted-foreground"
                        }`}
                      >
                        <Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <p
                          className={`font-medium ${
                            isCompleted || isActive
                              ? "text-foreground"
                              : "text-muted-foreground"
                          }`}
                        >
                          {status.label}
                        </p>
                        {isActive && (
                          <p className="text-sm text-primary-500">
                            {locale === "ar" ? "جاري الآن..." : "In progress..."}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </motion.div>

          {/* Contact Options */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="space-y-4"
          >
            {/* WhatsApp */}
            <a
              href={whatsappUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex w-full items-center justify-center gap-3 rounded-xl bg-green-600 px-6 py-4 font-medium text-white transition-colors hover:bg-green-700"
            >
              <MessageCircle className="h-5 w-5" />
              {t("contactWhatsapp")}
            </a>

            {/* Back to Home */}
            <Link href={`/${locale}`} className="block">
              <Button variant="outline" className="w-full" size="lg">
                <Home className="mr-2 h-5 w-5" />
                {t("backHome")}
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
