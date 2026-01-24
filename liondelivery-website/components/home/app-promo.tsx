"use client";

import { useTranslations } from "next-intl";
import { useLocale } from "next-intl";
import { motion } from "framer-motion";
import { MessageCircle, ArrowRight, Smartphone, Sparkles } from "lucide-react";
import { SITE_CONFIG } from "@/lib/utils/constants";

export function AppPromo() {
  const t = useTranslations("home.whatsapp");
  const locale = useLocale();

  const whatsappUrl = `https://wa.me/${SITE_CONFIG.contact.whatsapp.replace(/[^0-9]/g, "")}`;

  return (
    <section className="py-16 md:py-20">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-500 via-emerald-600 to-teal-600"
        >
          {/* Background Decorative Elements */}
          <div className="absolute inset-0 overflow-hidden">
            {/* Circles */}
            <div className="absolute -end-20 -top-20 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
            <div className="absolute -bottom-20 -start-20 h-64 w-64 rounded-full bg-white/10 blur-3xl" />

            {/* Pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute inset-0" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-rule='evenodd'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/svg%3E")`,
              }} />
            </div>
          </div>

          <div className="relative flex flex-col items-center gap-8 p-8 md:flex-row md:p-12 lg:p-16">
            {/* Icon Section */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="flex-shrink-0"
            >
              <div className="relative">
                {/* Glow Effect */}
                <div className="absolute inset-0 rounded-3xl bg-white/20 blur-xl" />

                {/* Icon Container */}
                <div className="relative flex h-28 w-28 items-center justify-center rounded-3xl bg-white/20 backdrop-blur-sm ring-1 ring-white/30 md:h-36 md:w-36">
                  <svg
                    className="h-16 w-16 text-white md:h-20 md:w-20"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                  </svg>
                </div>

                {/* Sparkle Badge */}
                <div className="absolute -end-2 -top-2 flex h-10 w-10 items-center justify-center rounded-full bg-amber-400 shadow-lg shadow-amber-400/30">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
              </div>
            </motion.div>

            {/* Content */}
            <div className="flex-1 text-center md:text-start">
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3 }}
                className="mb-3 text-2xl font-bold text-white md:text-3xl lg:text-4xl"
              >
                {t("title")}
              </motion.h2>
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.4 }}
                className="mb-8 text-white/80 md:text-lg"
              >
                {t("subtitle")}
              </motion.p>

              {/* CTA Button */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.5 }}
              >
                <a
                  href={whatsappUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group inline-flex items-center gap-3 rounded-full bg-white px-8 py-4 font-bold text-emerald-600 shadow-xl shadow-emerald-900/20 transition-all duration-300 hover:bg-emerald-50 hover:shadow-2xl hover:shadow-emerald-900/30 hover:scale-105 active:scale-100"
                >
                  <MessageCircle className="h-5 w-5" />
                  {t("button")}
                  <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1 rtl:group-hover:-translate-x-1 rtl:rotate-180" />
                </a>
              </motion.div>

              {/* Features */}
              <motion.div
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.6 }}
                className="mt-6 flex flex-wrap items-center justify-center gap-4 md:justify-start"
              >
                {[
                  locale === "ar" ? "رد سريع" : "Quick Response",
                  locale === "ar" ? "دعم 24/7" : "24/7 Support",
                  locale === "ar" ? "سهل الاستخدام" : "Easy to Use",
                ].map((feature, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1.5 text-sm text-white/70"
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-white/50" />
                    {feature}
                  </span>
                ))}
              </motion.div>
            </div>

            {/* Phone Mockup Placeholder */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="hidden lg:block"
            >
              <div className="relative">
                {/* Phone Frame */}
                <div className="flex h-64 w-32 items-center justify-center rounded-3xl bg-white/10 ring-1 ring-white/20 backdrop-blur-sm">
                  <Smartphone className="h-16 w-16 text-white/40" />
                </div>

                {/* Floating Message Bubble */}
                <div className="absolute -start-8 top-8 rounded-2xl bg-white px-4 py-2 shadow-xl">
                  <span className="text-2xl">👋</span>
                </div>

                {/* Floating Message Bubble 2 */}
                <div className="absolute -end-4 bottom-12 rounded-2xl bg-white px-4 py-2 shadow-xl">
                  <span className="text-2xl">🍕</span>
                </div>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
