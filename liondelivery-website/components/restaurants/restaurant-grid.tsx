"use client";

import { motion } from "framer-motion";
import { RestaurantCard } from "./restaurant-card";
import { RestaurantSkeleton } from "./restaurant-skeleton";
import type { Restaurant } from "@/types/restaurant";

interface RestaurantGridProps {
  restaurants: Restaurant[];
  isLoading?: boolean;
  skeletonCount?: number;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: "easeOut",
    },
  },
};

export function RestaurantGrid({
  restaurants,
  isLoading = false,
  skeletonCount = 8
}: RestaurantGridProps) {
  if (isLoading) {
    return (
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {Array.from({ length: skeletonCount }).map((_, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <RestaurantSkeleton />
          </motion.div>
        ))}
      </div>
    );
  }

  if (restaurants.length === 0) {
    return null;
  }

  return (
    <motion.div
      className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {restaurants.map((restaurant, index) => (
        <motion.div key={restaurant.id} variants={itemVariants}>
          <RestaurantCard
            restaurant={restaurant}
            index={0} // Disable internal animation since we're using container animation
          />
        </motion.div>
      ))}
    </motion.div>
  );
}
