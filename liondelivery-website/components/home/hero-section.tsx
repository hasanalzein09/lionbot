"use client";

import { useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { HeroSearch } from "./hero-search";
import { StatsSection } from "./stats-section";

export function HeroSection() {
  const t = useTranslations("home.hero");

  return (
    <section className="relative min-h-[85vh] overflow-hidden bg-gradient-to-br from-emerald-50 via-white to-rose-50">
      {/* Floating Decorative Orbs */}
      <motion.div
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 0.6, scale: 1 }}
        transition={{ duration: 1.5, ease: "easeOut" }}
        className="absolute -start-32 top-20 h-96 w-96 rounded-full bg-gradient-to-br from-emerald-400/30 to-emerald-500/20 blur-3xl"
      />
      <motion.div
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 0.5, scale: 1 }}
        transition={{ duration: 1.5, delay: 0.3, ease: "easeOut" }}
        className="absolute -end-32 bottom-20 h-80 w-80 rounded-full bg-gradient-to-br from-rose-400/30 to-rose-500/20 blur-3xl"
      />
      <motion.div
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 0.4, scale: 1 }}
        transition={{ duration: 1.5, delay: 0.6, ease: "easeOut" }}
        className="absolute end-1/4 top-1/4 h-64 w-64 rounded-full bg-gradient-to-br from-amber-300/20 to-amber-400/10 blur-3xl"
      />

      {/* Animated Floating Emojis */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 0.8 }}
        className="absolute start-[10%] top-[20%] text-4xl md:text-5xl"
      >
        <motion.span
          animate={{ y: [-10, 10, -10], rotate: [-5, 5, -5] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          className="inline-block"
        >
          🍕
        </motion.span>
      </motion.div>
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 1 }}
        className="absolute end-[15%] top-[25%] text-4xl md:text-5xl"
      >
        <motion.span
          animate={{ y: [10, -10, 10], rotate: [5, -5, 5] }}
          transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
          className="inline-block"
        >
          🍔
        </motion.span>
      </motion.div>
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 1.2 }}
        className="absolute start-[5%] bottom-[30%] text-3xl md:text-4xl"
      >
        <motion.span
          animate={{ y: [-8, 12, -8], rotate: [-3, 6, -3] }}
          transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut" }}
          className="inline-block"
        >
          🥗
        </motion.span>
      </motion.div>
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 1.4 }}
        className="absolute end-[8%] bottom-[35%] text-3xl md:text-4xl"
      >
        <motion.span
          animate={{ y: [8, -12, 8], rotate: [3, -6, 3] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
          className="inline-block"
        >
          🍜
        </motion.span>
      </motion.div>

      <div className="container relative z-10 mx-auto flex min-h-[85vh] items-center px-4 py-16 md:py-24">
        <div className="mx-auto max-w-4xl text-center">
          {/* Lion Emoji with Glow Effect */}
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", damping: 10, stiffness: 100 }}
            className="mb-8"
          >
            <span className="relative inline-block text-8xl md:text-9xl drop-shadow-2xl">
              <motion.span
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                className="inline-block"
              >
                🦁
              </motion.span>
            </span>
          </motion.div>

          {/* Title */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="mb-6 text-4xl font-extrabold leading-tight tracking-tight md:text-6xl lg:text-7xl"
          >
            <span className="bg-gradient-to-r from-emerald-600 via-emerald-500 to-teal-500 bg-clip-text text-transparent">
              {t("title")}
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="mb-10 text-lg text-gray-600 md:text-xl lg:text-2xl"
          >
            {t("subtitle")}
          </motion.p>

          {/* Search */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="mb-8"
          >
            <HeroSearch />
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.8 }}
            className="mt-16"
          >
            <StatsSection />
          </motion.div>
        </div>
      </div>

      {/* Bottom Wave */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg
          viewBox="0 0 1440 120"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full"
          preserveAspectRatio="none"
        >
          <path
            d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z"
            fill="white"
          />
        </svg>
      </div>
    </section>
  );
}
