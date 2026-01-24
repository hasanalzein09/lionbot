"use client";

import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { Facebook, Instagram, MapPin, Phone, Mail, ArrowUpRight } from "lucide-react";
import { SITE_CONFIG } from "@/lib/utils/constants";

export function Footer() {
  const t = useTranslations("common");
  const locale = useLocale();
  const currentYear = new Date().getFullYear();

  const quickLinks = [
    { href: `/${locale}/restaurants`, label: t("restaurants") },
    { href: `/${locale}/categories`, label: t("categories") },
    { href: `/${locale}/about`, label: t("about") },
  ];

  return (
    <footer className="bg-secondary-50 border-t border-secondary-200">
      <div className="container mx-auto px-4 py-12 lg:py-16">
        <div className="grid gap-10 md:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div className="space-y-5">
            <Link href={`/${locale}`} className="inline-flex items-center gap-2.5 group">
              <span className="text-3xl group-hover:animate-bounce-soft transition-transform">
                🦁
              </span>
              <span className="text-xl font-bold text-gradient">
                Lion Delivery
              </span>
            </Link>
            <p className="text-sm text-secondary-600 leading-relaxed max-w-xs">
              {locale === "ar"
                ? "أفضل خدمة توصيل طعام في صيدا. نوصل لك طعامك المفضل من أفضل المطاعم."
                : "The best food delivery service in Saida. We deliver your favorite food from the best restaurants."}
            </p>
            <div className="flex gap-3">
              <a
                href={SITE_CONFIG.social.facebook}
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-secondary-500 shadow-soft transition-all hover:text-primary-500 hover:shadow-md hover:-translate-y-0.5"
                aria-label="Facebook"
              >
                <Facebook className="h-4 w-4" />
              </a>
              <a
                href={SITE_CONFIG.social.instagram}
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-secondary-500 shadow-soft transition-all hover:text-primary-500 hover:shadow-md hover:-translate-y-0.5"
                aria-label="Instagram"
              >
                <Instagram className="h-4 w-4" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="mb-5 text-sm font-semibold uppercase tracking-wider text-secondary-900">
              {locale === "ar" ? "روابط سريعة" : "Quick Links"}
            </h3>
            <ul className="space-y-3">
              {quickLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="group inline-flex items-center gap-1 text-sm text-secondary-600 transition-colors hover:text-primary-500"
                  >
                    <span>{link.label}</span>
                    <ArrowUpRight className="h-3 w-3 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="mb-5 text-sm font-semibold uppercase tracking-wider text-secondary-900">
              {locale === "ar" ? "تواصل معنا" : "Contact Us"}
            </h3>
            <ul className="space-y-4">
              <li>
                <a
                  href={`tel:${SITE_CONFIG.contact.phone}`}
                  className="group flex items-center gap-3 text-sm text-secondary-600 transition-colors hover:text-primary-500"
                >
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white shadow-soft group-hover:shadow-md transition-shadow">
                    <Phone className="h-4 w-4" />
                  </span>
                  <span dir="ltr">{SITE_CONFIG.contact.phone}</span>
                </a>
              </li>
              <li>
                <a
                  href={`mailto:${SITE_CONFIG.contact.email}`}
                  className="group flex items-center gap-3 text-sm text-secondary-600 transition-colors hover:text-primary-500"
                >
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white shadow-soft group-hover:shadow-md transition-shadow">
                    <Mail className="h-4 w-4" />
                  </span>
                  <span>{SITE_CONFIG.contact.email}</span>
                </a>
              </li>
              <li>
                <div className="flex items-center gap-3 text-sm text-secondary-600">
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white shadow-soft">
                    <MapPin className="h-4 w-4" />
                  </span>
                  <span>
                    {locale === "ar" ? "صيدا، لبنان" : "Saida, Lebanon"}
                  </span>
                </div>
              </li>
            </ul>
          </div>

          {/* WhatsApp */}
          <div>
            <h3 className="mb-5 text-sm font-semibold uppercase tracking-wider text-secondary-900">
              {locale === "ar" ? "اطلب عبر واتساب" : "Order via WhatsApp"}
            </h3>
            <p className="mb-5 text-sm text-secondary-600 leading-relaxed">
              {locale === "ar"
                ? "تواصل معنا مباشرة عبر واتساب لأي استفسار أو طلب"
                : "Contact us directly via WhatsApp for any inquiry or order"}
            </p>
            <a
              href={`https://wa.me/${SITE_CONFIG.contact.whatsapp.replace(/[^0-9]/g, "")}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2.5 rounded-full bg-primary-500 px-5 py-2.5 text-sm font-medium text-white shadow-primary transition-all hover:bg-primary-600 hover:shadow-primary-lg hover:-translate-y-0.5 btn-press"
            >
              <svg
                className="h-5 w-5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
              </svg>
              <span>WhatsApp</span>
            </a>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-secondary-200">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <p className="text-center text-sm text-secondary-500">
              &copy; {currentYear} Lion Delivery.{" "}
              {locale === "ar" ? "جميع الحقوق محفوظة" : "All rights reserved"}
            </p>
            <p className="text-center text-xs text-secondary-400">
              {locale === "ar"
                ? "صنع بـ ❤️ في صيدا"
                : "Made with ❤️ in Saida"}
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
