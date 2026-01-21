import { Suspense } from "react";
import { notFound } from "next/navigation";
import { setRequestLocale } from "next-intl/server";
import { getTranslations } from "next-intl/server";
import type { Metadata } from "next";
import { RestaurantDetailContent } from "./restaurant-detail-content";
import { RestaurantDetailSkeleton } from "./restaurant-detail-skeleton";

interface RestaurantDetailPageProps {
  params: Promise<{ locale: string; slug: string }>;
}

export async function generateMetadata({
  params,
}: RestaurantDetailPageProps): Promise<Metadata> {
  const { locale, slug } = await params;
  // In production, fetch restaurant data for metadata
  const restaurantName = slug.replace(/-/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());

  return {
    title: restaurantName,
    description:
      locale === "ar"
        ? `اطلب من ${restaurantName} عبر Lion Delivery`
        : `Order from ${restaurantName} via Lion Delivery`,
  };
}

export default async function RestaurantDetailPage({
  params,
}: RestaurantDetailPageProps) {
  const { locale, slug } = await params;
  setRequestLocale(locale);

  return (
    <Suspense fallback={<RestaurantDetailSkeleton />}>
      <RestaurantDetailContent slug={slug} />
    </Suspense>
  );
}
