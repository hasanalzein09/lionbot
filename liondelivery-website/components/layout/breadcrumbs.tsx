"use client";

import Link from "next/link";
import { useLocale } from "next-intl";
import { ChevronLeft, ChevronRight, Home } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export function Breadcrumbs({ items }: BreadcrumbsProps) {
  const locale = useLocale();
  const isRTL = locale === "ar";
  const Chevron = isRTL ? ChevronLeft : ChevronRight;

  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex items-center gap-2 text-sm">
        {/* Home */}
        <li>
          <Link
            href={`/${locale}`}
            className="text-muted-foreground transition-colors hover:text-primary-500"
          >
            <Home className="h-4 w-4" />
          </Link>
        </li>

        {items.map((item, index) => (
          <li key={index} className="flex items-center gap-2">
            <Chevron className="h-4 w-4 text-muted-foreground" />
            {item.href ? (
              <Link
                href={item.href}
                className="text-muted-foreground transition-colors hover:text-primary-500"
              >
                {item.label}
              </Link>
            ) : (
              <span className="font-medium text-foreground">{item.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
