import { Suspense } from "react";
import { setRequestLocale } from "next-intl/server";
import { getTranslations } from "next-intl/server";
import type { Metadata } from "next";
import { RestaurantsContent } from "./restaurants-content";
import { RestaurantsSkeleton } from "./restaurants-skeleton";

interface RestaurantsPageProps {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export async function generateMetadata({
  params,
}: RestaurantsPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "restaurants" });

  return {
    title: t("title"),
    description: t("subtitle"),
  };
}

export default async function RestaurantsPage({
  params,
  searchParams,
}: RestaurantsPageProps) {
  const { locale } = await params;
  const resolvedSearchParams = await searchParams;
  setRequestLocale(locale);

  // Get initial filters from URL
  const category = resolvedSearchParams.category as string | undefined;
  const search = resolvedSearchParams.q as string | undefined;
  const sort = resolvedSearchParams.sort as string | undefined;

  return (
    <Suspense fallback={<RestaurantsSkeleton />}>
      <RestaurantsContent
        initialCategory={category}
        initialSearch={search}
        initialSort={sort}
      />
    </Suspense>
  );
}
