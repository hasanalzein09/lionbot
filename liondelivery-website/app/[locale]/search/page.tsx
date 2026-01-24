"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { Search, X, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { RestaurantGrid } from "@/components/restaurants";
import { useDebounce } from "@/lib/hooks/use-debounce";
import { useSearch } from "@/lib/hooks/use-search";

export default function SearchPage() {
  const locale = useLocale();
  const t = useTranslations("search");
  const router = useRouter();
  const searchParams = useSearchParams();

  const initialQuery = searchParams.get("q") || "";
  const [query, setQuery] = useState(initialQuery);
  const debouncedQuery = useDebounce(query, 300);

  // Use real API for search
  const { data: searchResults, isLoading, isFetching } = useSearch(debouncedQuery);

  // Get restaurants from search results
  const restaurants = searchResults?.restaurants || [];

  // Determine if we're searching (typing or fetching)
  const isSearching = query !== debouncedQuery || isFetching;

  // Update URL when query changes
  useEffect(() => {
    if (debouncedQuery) {
      router.replace(`/${locale}/search?q=${encodeURIComponent(debouncedQuery)}`, {
        scroll: false,
      });
    } else {
      router.replace(`/${locale}/search`, { scroll: false });
    }
  }, [debouncedQuery, locale, router]);

  const handleClear = () => {
    setQuery("");
  };

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="mb-2 text-2xl font-bold md:text-3xl">
            🔍 {t("title")}
          </h1>
        </motion.div>

        {/* Search Input */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <div className="relative">
            <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t("placeholder")}
              className="h-14 pl-12 pr-12 text-lg rounded-2xl"
              autoFocus
            />
            {query && (
              <button
                onClick={handleClear}
                className="absolute right-4 top-1/2 -translate-y-1/2 rounded-full p-1 text-muted-foreground transition-colors hover:bg-secondary-700 hover:text-foreground"
              >
                {isSearching ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <X className="h-5 w-5" />
                )}
              </button>
            )}
          </div>
        </motion.div>

        {/* Results */}
        {debouncedQuery ? (
          <>
            {/* Results Count */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-6"
            >
              <p className="text-muted-foreground">
                {restaurants.length}{" "}
                {locale === "ar" ? "نتيجة" : "results"}{" "}
                {locale === "ar" ? "لـ" : "for"} "{debouncedQuery}"
              </p>
            </motion.div>

            {isLoading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
              </div>
            ) : restaurants.length > 0 ? (
              <RestaurantGrid restaurants={restaurants} />
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="py-20 text-center"
              >
                <div className="mb-4 text-6xl">🔍</div>
                <h3 className="mb-2 text-xl font-semibold">
                  {t("noResults.title")}
                </h3>
                <p className="mb-6 text-muted-foreground">
                  {t("noResults.subtitle")}
                </p>
                <Button variant="outline" onClick={handleClear}>
                  {locale === "ar" ? "مسح البحث" : "Clear search"}
                </Button>
              </motion.div>
            )}
          </>
        ) : (
          /* Popular Searches */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="mb-4 text-lg font-semibold">{t("popular")}</h2>
            <div className="flex flex-wrap gap-2">
              {[
                locale === "ar" ? "برغر" : "Burger",
                locale === "ar" ? "شاورما" : "Shawarma",
                locale === "ar" ? "بيتزا" : "Pizza",
                locale === "ar" ? "قهوة" : "Coffee",
                locale === "ar" ? "حلويات" : "Sweets",
              ].map((term) => (
                <button
                  key={term}
                  onClick={() => setQuery(term)}
                  className="rounded-full bg-secondary-800 px-4 py-2 text-sm transition-colors hover:bg-primary-500 hover:text-white"
                >
                  {term}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
