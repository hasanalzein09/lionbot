"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";

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
    <form onSubmit={handleSubmit} className="mx-auto max-w-xl">
      <div className="relative flex items-center">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("searchPlaceholder")}
            className="h-14 w-full rounded-2xl border border-border bg-secondary-800/80 pl-12 pr-4 text-base backdrop-blur-sm transition-all placeholder:text-muted-foreground focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          />
        </div>
        <Button
          type="submit"
          size="lg"
          className="absolute right-2 h-10 rounded-xl px-6"
        >
          <Search className="h-4 w-4 md:mr-2" />
          <span className="hidden md:inline">
            {locale === "ar" ? "بحث" : "Search"}
          </span>
        </Button>
      </div>
    </form>
  );
}
