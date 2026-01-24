"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { useState, useEffect } from "react";
import { Menu, Search, ShoppingCart, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { LanguageSwitcher } from "./language-switcher";
import { MobileNav } from "./mobile-nav";
import { CartDrawer } from "./cart-drawer";
import { SearchModal } from "./search-modal";
import { useCartStore } from "@/lib/stores/cart-store";
import { cn } from "@/lib/utils/cn";

export function Header() {
  const t = useTranslations("common");
  const locale = useLocale();
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const cartItemsCount = useCartStore((state) => state.getTotalItems());

  // Handle scroll effect for shadow
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      <header
        className={cn(
          "sticky top-0 z-50 w-full transition-all duration-300",
          isScrolled
            ? "glass shadow-soft"
            : "bg-white/95 backdrop-blur-sm"
        )}
      >
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          {/* Logo */}
          <Link
            href={`/${locale}`}
            className="flex items-center gap-2.5 group"
          >
            <span className="text-2xl group-hover:animate-bounce-soft transition-transform">
              🦁
            </span>
            <span className="text-xl font-bold text-gradient">
              Lion Delivery
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden items-center gap-8 md:flex">
            <Link
              href={`/${locale}/restaurants`}
              className="relative text-sm font-medium text-secondary-600 transition-colors hover:text-primary-500 link-underline"
            >
              {t("restaurants")}
            </Link>
            <Link
              href={`/${locale}/about`}
              className="relative text-sm font-medium text-secondary-600 transition-colors hover:text-primary-500 link-underline"
            >
              {t("about")}
            </Link>
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-1 sm:gap-2">
            {/* Search Button */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSearchOpen(true)}
              className="hidden md:flex h-10 w-10 rounded-full text-secondary-600 hover:text-primary-500 hover:bg-primary-50 transition-all"
            >
              <Search className="h-5 w-5" />
              <span className="sr-only">{t("search")}</span>
            </Button>

            {/* Language Switcher */}
            <LanguageSwitcher />

            {/* Cart Button */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsCartOpen(true)}
              className="relative h-10 w-10 rounded-full text-secondary-600 hover:text-primary-500 hover:bg-primary-50 transition-all"
            >
              <ShoppingCart className="h-5 w-5" />
              {cartItemsCount > 0 && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute -end-0.5 -top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-primary-500 text-[10px] font-bold text-white shadow-primary"
                >
                  {cartItemsCount > 9 ? "9+" : cartItemsCount}
                </motion.span>
              )}
              <span className="sr-only">{t("cart")}</span>
            </Button>

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsMobileNavOpen(true)}
              className="md:hidden h-10 w-10 rounded-full text-secondary-600 hover:text-primary-500 hover:bg-primary-50 transition-all"
            >
              <Menu className="h-5 w-5" />
              <span className="sr-only">Menu</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Mobile Navigation */}
      <MobileNav
        isOpen={isMobileNavOpen}
        onClose={() => setIsMobileNavOpen(false)}
      />

      {/* Cart Drawer */}
      <CartDrawer isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />

      {/* Search Modal */}
      <SearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
      />
    </>
  );
}
