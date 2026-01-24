"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { Search, MapPin } from "lucide-react";

export function HeroSearch() {
  const t = useTranslations("home.hero");
  const locale = useLocale();
  const router = useRouter();
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/${locale}/search?q=${encodeURIComponent(query)}`);
    } else {
      router.push(`/${locale}/restaurants`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-2xl">
      <div className="relative">
        {/* Glassmorphism Container */}
        <div className="relative flex items-center rounded-full bg-white/80 p-2 shadow-xl shadow-emerald-500/10 backdrop-blur-xl ring-1 ring-gray-200/50 transition-all duration-300 focus-within:ring-2 focus-within:ring-emerald-500/50 focus-within:shadow-emerald-500/20">
          {/* Location Icon */}
          <div className="flex items-center ps-4">
            <MapPin className="h-5 w-5 text-emerald-500" />
          </div>

          {/* Search Input */}
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("searchPlaceholder")}
            className="h-12 flex-1 bg-transparent px-4 text-base text-gray-800 outline-none placeholder:text-gray-400"
          />

          {/* Search Button */}
          <button
            type="submit"
            className="flex h-12 items-center gap-2 rounded-full bg-gradient-to-r from-emerald-500 to-emerald-600 px-6 font-semibold text-white shadow-lg shadow-emerald-500/30 transition-all duration-300 hover:from-emerald-600 hover:to-emerald-700 hover:shadow-emerald-500/40 hover:scale-105 active:scale-100"
          >
            <Search className="h-5 w-5" />
            <span className="hidden sm:inline">
              {locale === "ar" ? "ابحث الآن" : "Search"}
            </span>
          </button>
        </div>

        {/* Quick Tags */}
        <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
          <span className="text-sm text-gray-500">
            {locale === "ar" ? "الاكثر بحثا:" : "Popular:"}
          </span>
          {["Pizza", "Burger", "Sushi", "Shawarma"].map((tag, index) => (
            <button
              key={tag}
              type="button"
              onClick={() => {
                setQuery(tag);
                router.push(`/${locale}/search?q=${encodeURIComponent(tag)}`);
              }}
              className="rounded-full bg-white/60 px-3 py-1.5 text-sm font-medium text-gray-600 ring-1 ring-gray-200/50 transition-all duration-200 hover:bg-emerald-50 hover:text-emerald-600 hover:ring-emerald-200"
            >
              {tag}
            </button>
          ))}
        </div>
      </div>
    </form>
  );
}
