"use client";

import { useLocale } from "next-intl";
import { useRouter, usePathname } from "next/navigation";
import { Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import { locales, type Locale } from "@/lib/i18n/config";

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const switchLocale = () => {
    const nextLocale = locale === "ar" ? "en" : "ar";

    // Replace the locale in the pathname
    const segments = pathname.split("/");
    segments[1] = nextLocale; // Replace the locale segment
    const newPath = segments.join("/");

    router.push(newPath);
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={switchLocale}
      className="gap-2"
    >
      <Globe className="h-4 w-4" />
      <span className="text-sm font-medium">
        {locale === "ar" ? "EN" : "عربي"}
      </span>
    </Button>
  );
}
