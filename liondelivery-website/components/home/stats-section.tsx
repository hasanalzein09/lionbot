"use client";

import { useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { UtensilsCrossed, ChefHat, Zap } from "lucide-react";

export function StatsSection() {
  const t = useTranslations("home.hero.stats");

  const stats = [
    {
      icon: UtensilsCrossed,
      value: "50+",
      label: t("restaurants"),
    },
    {
      icon: ChefHat,
      value: "1000+",
      label: t("dishes"),
    },
    {
      icon: Zap,
      value: "⚡",
      label: t("delivery"),
    },
  ];

  return (
    <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6 + index * 0.1 }}
            className="flex items-center gap-3"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-500/10">
              {stat.value === "⚡" ? (
                <span className="text-2xl">{stat.value}</span>
              ) : (
                <Icon className="h-6 w-6 text-primary-500" />
              )}
            </div>
            <div className="text-start">
              {stat.value !== "⚡" && (
                <p className="text-2xl font-bold text-primary-500">{stat.value}</p>
              )}
              <p className="text-sm text-muted-foreground">{stat.label}</p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
