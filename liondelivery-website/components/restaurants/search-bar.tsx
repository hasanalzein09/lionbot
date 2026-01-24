"use client";

import { useState, useEffect } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Search, X } from "lucide-react";
import { useDebounce } from "@/lib/hooks/use-debounce";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchBar({ value, onChange, placeholder }: SearchBarProps) {
  const locale = useLocale();
  const t = useTranslations("restaurants");
  const isRTL = locale === "ar";
  const [localValue, setLocalValue] = useState(value);
  const debouncedValue = useDebounce(localValue, 300);

  // Sync local value with prop
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  // Trigger onChange when debounced value changes
  useEffect(() => {
    if (debouncedValue !== value) {
      onChange(debouncedValue);
    }
  }, [debouncedValue, value, onChange]);

  const handleClear = () => {
    setLocalValue("");
    onChange("");
  };

  return (
    <div className="relative">
      {/* Search Icon */}
      <div className={`absolute top-1/2 -translate-y-1/2 ${isRTL ? "right-4" : "left-4"}`}>
        <Search className="h-5 w-5 text-emerald-500" />
      </div>

      {/* Input */}
      <input
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder={placeholder || t("searchPlaceholder")}
        className={`
          w-full h-12 bg-white rounded-full border border-gray-200
          shadow-sm hover:shadow-md focus:shadow-md
          text-gray-900 placeholder:text-gray-400
          outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500
          transition-all duration-200
          ${isRTL ? "pr-12 pl-10" : "pl-12 pr-10"}
        `}
        dir={isRTL ? "rtl" : "ltr"}
      />

      {/* Clear Button */}
      {localValue && (
        <button
          onClick={handleClear}
          className={`
            absolute top-1/2 -translate-y-1/2
            rounded-full p-1.5
            text-gray-400 hover:text-gray-600
            hover:bg-gray-100
            transition-colors duration-200
            ${isRTL ? "left-3" : "right-3"}
          `}
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
