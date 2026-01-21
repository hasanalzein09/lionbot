"use client";

import Link from "next/link";
import Image from "next/image";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { Star, Clock, MapPin, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { Restaurant } from "@/types/restaurant";

// Mock data - will be replaced with API data
const mockRestaurants: Restaurant[] = [
  {
    id: "1",
    name: "Burgero",
    nameAr: "برغيرو",
    slug: "burgero",
    description: "Best burgers in town",
    descriptionAr: "أفضل برغر في المدينة",
    image: "/images/placeholder-restaurant.webp",
    category: "Burger",
    categoryAr: "برغر",
    rating: 4.8,
    reviewCount: 120,
    priceRange: "$$",
    deliveryTime: { min: 25, max: 35 },
    isOpen: true,
    isFeatured: true,
  },
  {
    id: "2",
    name: "Baba Ghanouj",
    nameAr: "بابا غنوج",
    slug: "baba-ghanouj",
    description: "Authentic Lebanese grills",
    descriptionAr: "مشاوي لبنانية أصيلة",
    image: "/images/placeholder-restaurant.webp",
    category: "Grills",
    categoryAr: "مشاوي",
    rating: 4.9,
    reviewCount: 200,
    priceRange: "$$$",
    deliveryTime: { min: 30, max: 45 },
    isOpen: true,
    isFeatured: true,
  },
  {
    id: "3",
    name: "Twist Cafe",
    nameAr: "تويست كافيه",
    slug: "twist-cafe",
    description: "Premium coffee and desserts",
    descriptionAr: "قهوة فاخرة وحلويات",
    image: "/images/placeholder-restaurant.webp",
    category: "Coffee",
    categoryAr: "قهوة",
    rating: 4.7,
    reviewCount: 85,
    priceRange: "$$",
    deliveryTime: { min: 15, max: 25 },
    isOpen: false,
    isFeatured: true,
  },
  {
    id: "4",
    name: "Submarine",
    nameAr: "صب مارين",
    slug: "submarine",
    description: "Delicious sandwiches",
    descriptionAr: "ساندويتشات لذيذة",
    image: "/images/placeholder-restaurant.webp",
    category: "Sandwich",
    categoryAr: "ساندويش",
    rating: 4.5,
    reviewCount: 95,
    priceRange: "$$",
    deliveryTime: { min: 20, max: 30 },
    isOpen: true,
    isFeatured: true,
  },
];

interface FeaturedRestaurantsProps {
  restaurants?: Restaurant[];
}

export function FeaturedRestaurants({ restaurants = mockRestaurants }: FeaturedRestaurantsProps) {
  const t = useTranslations("home.featured");
  const tCommon = useTranslations("common");
  const tRestaurants = useTranslations("restaurants");
  const locale = useLocale();

  return (
    <section className="py-12 md:py-16">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <motion.h2
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="text-2xl font-bold md:text-3xl"
          >
            ⭐ {t("title")}
          </motion.h2>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <Link href={`/${locale}/restaurants`}>
              <Button variant="ghost" className="group">
                {tCommon("viewAll")}
                {locale === "ar" ? (
                  <ChevronLeft className="ms-1 h-4 w-4 transition-transform group-hover:-translate-x-1" />
                ) : (
                  <ChevronRight className="ms-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
                )}
              </Button>
            </Link>
          </motion.div>
        </div>

        {/* Grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {restaurants.map((restaurant, index) => (
            <RestaurantCard
              key={restaurant.id}
              restaurant={restaurant}
              locale={locale}
              index={index}
              tRestaurants={tRestaurants}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

interface RestaurantCardProps {
  restaurant: Restaurant;
  locale: string;
  index: number;
  tRestaurants: ReturnType<typeof useTranslations>;
}

function RestaurantCard({ restaurant, locale, index, tRestaurants }: RestaurantCardProps) {
  const displayName = locale === "ar" && restaurant.nameAr ? restaurant.nameAr : restaurant.name;
  const displayCategory = locale === "ar" && restaurant.categoryAr ? restaurant.categoryAr : restaurant.category;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.1 }}
    >
      <Link href={`/${locale}/restaurants/${restaurant.slug}`}>
        <div className="group overflow-hidden rounded-2xl bg-secondary-800 transition-all hover:shadow-xl hover:shadow-primary-500/10">
          {/* Image */}
          <div className="relative aspect-[4/3] overflow-hidden">
            <Image
              src={restaurant.image || "/images/placeholder-restaurant.webp"}
              alt={displayName}
              fill
              className="object-cover transition-transform duration-300 group-hover:scale-110"
            />

            {/* Status Badge */}
            <div className="absolute left-3 top-3">
              <Badge variant={restaurant.isOpen ? "success" : "secondary"}>
                {restaurant.isOpen ? tRestaurants("openNow") : tRestaurants("closed")}
              </Badge>
            </div>

            {/* Featured Badge */}
            {restaurant.isFeatured && (
              <div className="absolute right-3 top-3">
                <Badge variant="warning">🔥</Badge>
              </div>
            )}

            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
          </div>

          {/* Content */}
          <div className="p-4">
            <div className="mb-2 flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-foreground group-hover:text-primary-500 transition-colors line-clamp-1">
                  {displayName}
                </h3>
                <p className="text-sm text-muted-foreground">{displayCategory}</p>
              </div>
              {restaurant.rating && (
                <div className="flex items-center gap-1 rounded-lg bg-primary-500/10 px-2 py-1">
                  <Star className="h-3 w-3 fill-primary-500 text-primary-500" />
                  <span className="text-sm font-medium text-primary-500">
                    {restaurant.rating}
                  </span>
                </div>
              )}
            </div>

            {/* Meta */}
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              {restaurant.deliveryTime && (
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {restaurant.deliveryTime.min}-{restaurant.deliveryTime.max}{" "}
                  {locale === "ar" ? "د" : "min"}
                </span>
              )}
              {restaurant.priceRange && (
                <span className="text-primary-500">{restaurant.priceRange}</span>
              )}
            </div>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}
