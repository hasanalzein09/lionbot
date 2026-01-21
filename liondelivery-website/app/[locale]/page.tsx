import { setRequestLocale } from "next-intl/server";
import { HeroSection } from "@/components/home/hero-section";
import { CategoriesSlider } from "@/components/home/categories-slider";
import { FeaturedRestaurants } from "@/components/home/featured-restaurants";
import { HowItWorks } from "@/components/home/how-it-works";
import { AppPromo } from "@/components/home/app-promo";

interface HomePageProps {
  params: Promise<{ locale: string }>;
}

export default async function HomePage({ params }: HomePageProps) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <>
      <HeroSection />
      <CategoriesSlider />
      <FeaturedRestaurants />
      <HowItWorks />
      <AppPromo />
    </>
  );
}
