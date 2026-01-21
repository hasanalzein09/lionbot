"use client";

import { useEffect } from "react";
import { useLocale } from "next-intl";
import { motion } from "framer-motion";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  const locale = useLocale();

  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center py-20">
      <div className="container mx-auto px-4 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mx-auto max-w-md"
        >
          {/* Error Icon */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", damping: 10, delay: 0.2 }}
            className="mb-6 inline-flex h-24 w-24 items-center justify-center rounded-full bg-error-500/20"
          >
            <AlertTriangle className="h-12 w-12 text-error-500" />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h1 className="mb-4 text-2xl font-bold md:text-3xl">
              {locale === "ar" ? "حدث خطأ" : "Something went wrong!"}
            </h1>
            <p className="mb-8 text-muted-foreground">
              {locale === "ar"
                ? "عذراً، حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى."
                : "Sorry, an unexpected error occurred. Please try again."}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Button onClick={reset} size="lg">
              <RefreshCw className="mr-2 h-5 w-5" />
              {locale === "ar" ? "إعادة المحاولة" : "Try again"}
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
