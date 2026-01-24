"use client";

import { useState, useRef, useEffect } from "react";
import { useLocale, useTranslations } from "next-intl";
import { ChevronDown, Check } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils/cn";

export type SortOption = "newest" | "rating" | "popular";

interface SortDropdownProps {
  value: SortOption;
  onChange: (value: SortOption) => void;
}

export function SortDropdown({ value, onChange }: SortDropdownProps) {
  const locale = useLocale();
  const t = useTranslations("restaurants.filters");
  const isRTL = locale === "ar";
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const options: { value: SortOption; label: string }[] = [
    { value: "newest", label: t("newest") },
    { value: "rating", label: t("rating") },
    { value: "popular", label: t("mostOrdered") },
  ];

  const selectedOption = options.find((opt) => opt.value === value);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={dropdownRef} className="relative">
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 rounded-full bg-white px-4 py-2.5",
          "text-sm font-medium text-gray-700",
          "border border-gray-200 shadow-sm",
          "hover:shadow-md hover:border-gray-300",
          "transition-all duration-200",
          isOpen && "border-emerald-500 ring-2 ring-emerald-500/20"
        )}
      >
        <span className="text-gray-500">{t("sortBy")}:</span>
        <span className="text-gray-900">{selectedOption?.label}</span>
        <ChevronDown
          className={cn(
            "h-4 w-4 text-gray-400 transition-transform duration-200",
            isOpen && "rotate-180"
          )}
        />
      </button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className={cn(
              "absolute top-full z-20 mt-2 min-w-[180px]",
              "overflow-hidden rounded-xl bg-white",
              "border border-gray-100 shadow-lg",
              isRTL ? "left-0" : "right-0"
            )}
          >
            <div className="py-1">
              {options.map((option) => {
                const isSelected = value === option.value;
                return (
                  <button
                    key={option.value}
                    onClick={() => {
                      onChange(option.value);
                      setIsOpen(false);
                    }}
                    className={cn(
                      "flex w-full items-center justify-between px-4 py-2.5 text-sm",
                      "transition-colors duration-150",
                      isSelected
                        ? "bg-emerald-50 text-emerald-600"
                        : "text-gray-700 hover:bg-gray-50"
                    )}
                  >
                    <span className={isSelected ? "font-medium" : ""}>
                      {option.label}
                    </span>
                    {isSelected && (
                      <Check className="h-4 w-4 text-emerald-500" />
                    )}
                  </button>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
