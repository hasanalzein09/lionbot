"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { usePathname } from "next/navigation";
import { X, Home, UtensilsCrossed, Info, Search, Phone } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { LanguageSwitcher } from "./language-switcher";

interface MobileNavProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileNav({ isOpen, onClose }: MobileNavProps) {
  const t = useTranslations("common");
  const locale = useLocale();
  const pathname = usePathname();

  const navItems = [
    { href: `/${locale}`, label: t("home"), icon: Home },
    { href: `/${locale}/restaurants`, label: t("restaurants"), icon: UtensilsCrossed },
    { href: `/${locale}/search`, label: t("search"), icon: Search },
    { href: `/${locale}/about`, label: t("about"), icon: Info },
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

          {/* Drawer */}
          <motion.div
            initial={{ x: locale === "ar" ? "100%" : "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: locale === "ar" ? "100%" : "-100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className={`fixed inset-y-0 z-50 w-[280px] bg-secondary-900 shadow-xl ${
              locale === "ar" ? "right-0" : "left-0"
            }`}
          >
            <div className="flex h-full flex-col">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-border p-4">
                <Link
                  href={`/${locale}`}
                  onClick={onClose}
                  className="flex items-center gap-2"
                >
                  <span className="text-2xl">🦁</span>
                  <span className="font-bold text-primary-500">Lion Delivery</span>
                </Link>
                <Button variant="ghost" size="icon" onClick={onClose}>
                  <X className="h-5 w-5" />
                </Button>
              </div>

              {/* Navigation Links */}
              <nav className="flex-1 overflow-y-auto p-4">
                <ul className="space-y-2">
                  {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;
                    return (
                      <li key={item.href}>
                        <Link
                          href={item.href}
                          onClick={onClose}
                          className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
                            isActive
                              ? "bg-primary-500/10 text-primary-500"
                              : "text-foreground/80 hover:bg-secondary-800 hover:text-foreground"
                          }`}
                        >
                          <Icon className="h-5 w-5" />
                          <span>{item.label}</span>
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </nav>

              {/* Footer */}
              <div className="border-t border-border p-4 space-y-4">
                {/* Language Switcher */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    {locale === "ar" ? "اللغة" : "Language"}
                  </span>
                  <LanguageSwitcher />
                </div>

                {/* WhatsApp Contact */}
                <a
                  href="https://wa.me/96170000000"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 rounded-xl bg-green-600 px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-green-700"
                >
                  <Phone className="h-4 w-4" />
                  <span>
                    {locale === "ar" ? "تواصل معنا" : "Contact Us"}
                  </span>
                </a>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
