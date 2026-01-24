"use client";

import { useTranslations } from "next-intl";
import { useLocale } from "next-intl";
import { motion } from "framer-motion";
import { Search, ShoppingCart, Truck } from "lucide-react";

export function HowItWorks() {
  const t = useTranslations("home.howItWorks");
  const locale = useLocale();

  const steps = [
    {
      icon: Search,
      title: t("step1.title"),
      description: t("step1.description"),
      emoji: "🔍",
      color: "bg-emerald-100",
      iconColor: "text-emerald-600",
    },
    {
      icon: ShoppingCart,
      title: t("step2.title"),
      description: t("step2.description"),
      emoji: "🛒",
      color: "bg-rose-100",
      iconColor: "text-rose-600",
    },
    {
      icon: Truck,
      title: t("step3.title"),
      description: t("step3.description"),
      emoji: "🚗",
      color: "bg-amber-100",
      iconColor: "text-amber-600",
    },
  ];

  return (
    <section className="bg-gradient-to-b from-gray-50 to-white py-16 md:py-24">
      <div className="container mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-16 text-center"
        >
          <span className="mb-3 inline-block rounded-full bg-emerald-100 px-4 py-1.5 text-sm font-semibold text-emerald-700">
            {locale === "ar" ? "كيف يعمل" : "How It Works"}
          </span>
          <h2 className="text-3xl font-bold text-gray-900 md:text-4xl">
            {t("title")}
          </h2>
        </motion.div>

        {/* Steps */}
        <div className="relative">
          {/* Connection Line - Desktop */}
          <div className="absolute top-20 hidden h-1 w-full md:block">
            <div className="mx-auto flex h-full max-w-3xl items-center justify-between px-24">
              <motion.div
                initial={{ scaleX: 0 }}
                whileInView={{ scaleX: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: 0.5 }}
                className="h-0.5 flex-1 origin-left bg-gradient-to-r from-emerald-300 via-rose-300 to-amber-300"
              />
            </div>
          </div>

          <div className="grid gap-8 md:grid-cols-3 md:gap-12">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2 }}
                className="relative text-center"
              >
                {/* Step Card */}
                <div className="group">
                  {/* Icon Container */}
                  <div className="relative mx-auto mb-6">
                    {/* Background Glow */}
                    <div className={`absolute inset-0 ${step.color} rounded-3xl blur-xl opacity-50 transition-all duration-300 group-hover:opacity-70`} />

                    {/* Icon Box */}
                    <div className={`relative flex h-28 w-28 items-center justify-center rounded-3xl ${step.color} mx-auto shadow-lg ring-1 ring-white transition-all duration-300 group-hover:-translate-y-2 group-hover:shadow-xl`}>
                      <span className="text-5xl transition-transform duration-300 group-hover:scale-110">
                        {step.emoji}
                      </span>
                    </div>

                    {/* Step Number Badge */}
                    <div className="absolute -bottom-3 -end-3 flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-emerald-600 text-lg font-bold text-white shadow-lg shadow-emerald-500/30 ring-4 ring-white">
                      {index + 1}
                    </div>
                  </div>

                  {/* Content */}
                  <h3 className="mb-3 text-xl font-bold text-gray-900">
                    {step.title}
                  </h3>
                  <p className="mx-auto max-w-xs text-gray-500 leading-relaxed">
                    {step.description}
                  </p>
                </div>

                {/* Mobile Connection Line */}
                {index < steps.length - 1 && (
                  <div className="my-6 flex justify-center md:hidden">
                    <div className="h-12 w-0.5 bg-gradient-to-b from-gray-200 to-gray-300" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
