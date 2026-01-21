"use client";

import { useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { Search, ShoppingCart, Truck } from "lucide-react";

export function HowItWorks() {
  const t = useTranslations("home.howItWorks");

  const steps = [
    {
      icon: Search,
      title: t("step1.title"),
      description: t("step1.description"),
      emoji: "🔍",
    },
    {
      icon: ShoppingCart,
      title: t("step2.title"),
      description: t("step2.description"),
      emoji: "🛒",
    },
    {
      icon: Truck,
      title: t("step3.title"),
      description: t("step3.description"),
      emoji: "🚗",
    },
  ];

  return (
    <section className="bg-secondary-900/50 py-16 md:py-20">
      <div className="container mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-12 text-center"
        >
          <h2 className="text-2xl font-bold md:text-3xl">
            🚀 {t("title")}
          </h2>
        </motion.div>

        {/* Steps */}
        <div className="relative">
          {/* Connection Line */}
          <div className="absolute left-1/2 top-12 hidden h-0.5 w-[60%] -translate-x-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent md:block" />

          <div className="grid gap-8 md:grid-cols-3">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2 }}
                className="relative text-center"
              >
                {/* Step Number */}
                <div className="mb-4 flex justify-center">
                  <div className="relative">
                    <div className="flex h-24 w-24 items-center justify-center rounded-2xl bg-secondary-800 text-5xl shadow-lg transition-transform hover:scale-110">
                      {step.emoji}
                    </div>
                    <div className="absolute -bottom-2 -right-2 flex h-8 w-8 items-center justify-center rounded-full bg-primary-500 text-sm font-bold text-white shadow-lg">
                      {index + 1}
                    </div>
                  </div>
                </div>

                {/* Content */}
                <h3 className="mb-2 text-lg font-semibold">{step.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
