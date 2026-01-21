"use client";

import { use } from "react";
import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
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
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { SITE_CONFIG } from "@/lib/utils/constants";

interface OrderPageProps {
  params: Promise<{ locale: string; id: string }>;
}

export default function OrderPage({ params }: OrderPageProps) {
  const { locale, id: orderId } = use(params);
  const t = useTranslations("order");

  // In production, fetch order data
  // const { data: order } = useOrder(orderId);

  const orderStatuses = [
    {
      id: "confirmed",
      label: t("status.confirmed"),
      icon: CheckCircle,
      completed: true,
    },
    {
      id: "preparing",
      label: t("status.preparing"),
      icon: ChefHat,
      completed: false,
      active: true,
    },
    {
      id: "ready",
      label: t("status.ready"),
      icon: Package,
      completed: false,
    },
    {
      id: "delivering",
      label: t("status.delivering"),
      icon: Truck,
      completed: false,
    },
  ];

  const whatsappUrl = `https://wa.me/${SITE_CONFIG.contact.whatsapp.replace(/[^0-9]/g, "")}?text=${encodeURIComponent(
    locale === "ar"
      ? `مرحباً، أريد الاستفسار عن طلبي رقم ${orderId}`
      : `Hello, I want to inquire about my order ${orderId}`
  )}`;

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
              ✅ {t("success.title")}
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-muted-foreground"
            >
              {t("success.orderNumber")}:{" "}
              <span className="font-mono font-semibold text-primary-500">
                #{orderId}
              </span>
            </motion.p>
          </div>

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
                {orderStatuses.map((status, index) => {
                  const Icon = status.icon;
                  return (
                    <div key={status.id} className="relative flex items-center gap-4">
                      <div
                        className={`relative z-10 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full ${
                          status.completed
                            ? "bg-success-500 text-white"
                            : status.active
                            ? "bg-primary-500 text-white"
                            : "bg-secondary-700 text-muted-foreground"
                        }`}
                      >
                        <Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <p
                          className={`font-medium ${
                            status.completed || status.active
                              ? "text-foreground"
                              : "text-muted-foreground"
                          }`}
                        >
                          {status.label}
                        </p>
                        {status.active && (
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
