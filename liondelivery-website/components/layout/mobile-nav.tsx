"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { usePathname } from "next/navigation";
import { X, Home, UtensilsCrossed, Info, Search, Phone, ChevronRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { LanguageSwitcher } from "./language-switcher";
import { SITE_CONFIG } from "@/lib/utils/constants";

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
            className="fixed inset-0 z-50 bg-secondary-900/20 backdrop-blur-sm"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: locale === "ar" ? "100%" : "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: locale === "ar" ? "100%" : "-100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className={`fixed inset-y-0 z-50 w-[300px] bg-white shadow-elevated ${
              locale === "ar" ? "right-0" : "left-0"
            }`}
          >
            <div className="flex h-full flex-col">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-secondary-100 p-4">
                <Link
                  href={`/${locale}`}
                  onClick={onClose}
                  className="flex items-center gap-2.5 group"
                >
                  <span className="text-2xl group-hover:animate-bounce-soft">
                    🦁
                  </span>
                  <span className="font-bold text-gradient">Lion Delivery</span>
                </Link>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onClose}
                  className="h-9 w-9 rounded-full text-secondary-500 hover:text-secondary-700 hover:bg-secondary-100"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>

              {/* Navigation Links */}
              <nav className="flex-1 overflow-y-auto p-4">
                <ul className="space-y-1">
                  {navItems.map((item, index) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;
                    return (
                      <motion.li
                        key={item.href}
                        initial={{ opacity: 0, x: locale === "ar" ? 20 : -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        <Link
                          href={item.href}
                          onClick={onClose}
                          className={`group flex items-center justify-between rounded-xl px-4 py-3.5 text-sm font-medium transition-all ${
                            isActive
                              ? "bg-primary-50 text-primary-600"
                              : "text-secondary-700 hover:bg-secondary-50 hover:text-secondary-900"
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <span
                              className={`flex h-9 w-9 items-center justify-center rounded-lg transition-colors ${
                                isActive
                                  ? "bg-primary-100 text-primary-600"
                                  : "bg-secondary-100 text-secondary-500 group-hover:bg-secondary-200"
                              }`}
                            >
                              <Icon className="h-4.5 w-4.5" />
                            </span>
                            <span>{item.label}</span>
                          </div>
                          <ChevronRight
                            className={`h-4 w-4 transition-all ${
                              isActive
                                ? "text-primary-400"
                                : "text-secondary-300 group-hover:text-secondary-400 group-hover:translate-x-0.5 rtl:group-hover:-translate-x-0.5"
                            }`}
                          />
                        </Link>
                      </motion.li>
                    );
                  })}
                </ul>
              </nav>

              {/* Footer */}
              <div className="border-t border-secondary-100 p-4 space-y-4 bg-secondary-50/50">
                {/* Language Switcher */}
                <div className="flex items-center justify-between rounded-xl bg-white p-3 shadow-soft">
                  <span className="text-sm font-medium text-secondary-600">
                    {locale === "ar" ? "اللغة" : "Language"}
                  </span>
                  <LanguageSwitcher />
                </div>

                {/* WhatsApp Contact */}
                <a
                  href={`https://wa.me/${SITE_CONFIG?.contact?.whatsapp?.replace(/[^0-9]/g, "") || "96170000000"}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2.5 rounded-xl bg-primary-500 px-4 py-3.5 text-sm font-medium text-white shadow-primary transition-all hover:bg-primary-600 hover:shadow-primary-lg btn-press"
                >
                  <svg
                    className="h-5 w-5"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                  </svg>
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
