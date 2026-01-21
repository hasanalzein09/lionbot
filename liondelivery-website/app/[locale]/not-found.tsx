"use client";

import Link from "next/link";
import { useLocale } from "next-intl";
import { motion } from "framer-motion";
import { Home, Search } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  const locale = useLocale();

  return (
    <div className="min-h-screen bg-background flex items-center justify-center py-20">
      <div className="container mx-auto px-4 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mx-auto max-w-md"
        >
          {/* 404 */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", damping: 10, delay: 0.2 }}
            className="mb-8 text-9xl font-bold text-primary-500/20"
          >
            404
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h1 className="mb-4 text-2xl font-bold md:text-3xl">
              {locale === "ar" ? "الصفحة غير موجودة" : "Page Not Found"}
            </h1>
            <p className="mb-8 text-muted-foreground">
              {locale === "ar"
                ? "عذراً، الصفحة التي تبحث عنها غير موجودة أو تم نقلها."
                : "Sorry, the page you're looking for doesn't exist or has been moved."}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="flex flex-col gap-3 sm:flex-row sm:justify-center"
          >
            <Button asChild size="lg">
              <Link href={`/${locale}`}>
                <Home className="mr-2 h-5 w-5" />
                {locale === "ar" ? "الرئيسية" : "Home"}
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href={`/${locale}/restaurants`}>
                <Search className="mr-2 h-5 w-5" />
                {locale === "ar" ? "تصفح المطاعم" : "Browse Restaurants"}
              </Link>
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
