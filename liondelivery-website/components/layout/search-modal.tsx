"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { Search, X, Clock, TrendingUp, ArrowRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const t = useTranslations("search");
  const locale = useLocale();
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  // Load recent searches from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("lion-recent-searches");
    if (saved) {
      setRecentSearches(JSON.parse(saved));
    }
  }, []);

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  // Handle keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (!isOpen) {
          // Open search - you'd need to lift this state up or use a store
        }
      }
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  const handleSearch = (searchQuery: string) => {
    if (!searchQuery.trim()) return;

    // Save to recent searches
    const updated = [searchQuery, ...recentSearches.filter((s) => s !== searchQuery)].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem("lion-recent-searches", JSON.stringify(updated));

    // Navigate to search page
    router.push(`/${locale}/search?q=${encodeURIComponent(searchQuery)}`);
    onClose();
    setQuery("");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(query);
  };

  const clearRecentSearches = () => {
    setRecentSearches([]);
    localStorage.removeItem("lion-recent-searches");
  };

  const popularSearches = [
    locale === "ar" ? "برغر" : "Burger",
    locale === "ar" ? "شاورما" : "Shawarma",
    locale === "ar" ? "بيتزا" : "Pizza",
    locale === "ar" ? "سوشي" : "Sushi",
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed left-1/2 top-20 z-50 w-full max-w-lg -translate-x-1/2 px-4"
          >
            <div className="overflow-hidden rounded-2xl bg-secondary-900 shadow-2xl">
              {/* Search Input */}
              <form onSubmit={handleSubmit} className="relative">
                <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
                <Input
                  ref={inputRef}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={t("placeholder")}
                  className="h-14 rounded-none border-0 border-b border-border bg-transparent pl-12 pr-12 text-lg focus:ring-0"
                />
                {query && (
                  <button
                    type="button"
                    onClick={() => setQuery("")}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    <X className="h-5 w-5" />
                  </button>
                )}
              </form>

              {/* Content */}
              <div className="max-h-[60vh] overflow-y-auto p-4">
                {/* Recent Searches */}
                {recentSearches.length > 0 && (
                  <div className="mb-6">
                    <div className="mb-3 flex items-center justify-between">
                      <h3 className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        {t("recent")}
                      </h3>
                      <button
                        onClick={clearRecentSearches}
                        className="text-xs text-primary-500 hover:text-primary-400"
                      >
                        {t("clear")}
                      </button>
                    </div>
                    <ul className="space-y-1">
                      {recentSearches.map((search, index) => (
                        <li key={index}>
                          <button
                            onClick={() => handleSearch(search)}
                            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-secondary-800"
                          >
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            <span>{search}</span>
                            <ArrowRight className="ms-auto h-4 w-4 text-muted-foreground" />
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Popular Searches */}
                <div>
                  <h3 className="mb-3 flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <TrendingUp className="h-4 w-4" />
                    {t("popular")}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {popularSearches.map((search, index) => (
                      <button
                        key={index}
                        onClick={() => handleSearch(search)}
                        className="rounded-full bg-secondary-800 px-4 py-2 text-sm transition-colors hover:bg-primary-500 hover:text-white"
                      >
                        {search}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="border-t border-border bg-secondary-800/50 px-4 py-3">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>
                    {locale === "ar" ? "اضغط Enter للبحث" : "Press Enter to search"}
                  </span>
                  <span>
                    <kbd className="rounded bg-secondary-700 px-1.5 py-0.5 text-xs">ESC</kbd>
                    {" "}
                    {locale === "ar" ? "للإغلاق" : "to close"}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
