import type { Metadata } from "next";
import { IBM_Plex_Sans_Arabic } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { getMessages, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { locales, localeDirection, type Locale } from "@/lib/i18n/config";
import { Providers } from "../providers";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import "../globals.css";

const ibmPlexArabic = IBM_Plex_Sans_Arabic({
  subsets: ["arabic", "latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-ibm-plex-arabic",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://liondelivery-saida.com"),
  title: {
    default: "Lion Delivery صيدا | اطلب طعامك المفضل أونلاين",
    template: "%s | Lion Delivery",
  },
  description:
    "أطلب من أفضل مطاعم صيدا - برغر، شاورما، بيتزا، حلويات والمزيد. توصيل سريع لباب منزلك.",
  keywords: [
    "توصيل طعام",
    "مطاعم صيدا",
    "طلب أونلاين",
    "delivery",
    "food",
    "Saida",
    "Lebanon",
  ],
  authors: [{ name: "Lion Delivery" }],
  creator: "Lion Delivery",
  publisher: "Lion Delivery",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  openGraph: {
    type: "website",
    locale: "ar_LB",
    alternateLocale: "en_US",
    url: "https://liondelivery-saida.com",
    siteName: "Lion Delivery",
    title: "Lion Delivery صيدا | اطلب طعامك المفضل",
    description: "أفضل خدمة توصيل طعام في صيدا",
    images: [
      {
        url: "/images/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "Lion Delivery",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Lion Delivery صيدا",
    description: "اطلب طعامك المفضل أونلاين",
    images: ["/images/og-image.jpg"],
  },
};

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

interface RootLayoutProps {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}

export default async function RootLayout({
  children,
  params,
}: RootLayoutProps) {
  const { locale } = await params;

  // Validate locale
  if (!locales.includes(locale as Locale)) {
    notFound();
  }

  // Enable static rendering
  setRequestLocale(locale);

  // Get messages for the locale
  const messages = await getMessages();

  const direction = localeDirection[locale as Locale];

  return (
    <html lang={locale} dir={direction} suppressHydrationWarning>
      <body
        className={`${ibmPlexArabic.variable} font-sans antialiased min-h-screen bg-background text-foreground`}
      >
        <NextIntlClientProvider messages={messages}>
          <Providers>
            <div className="flex min-h-screen flex-col">
              <Header />
              <main className="flex-1">{children}</main>
              <Footer />
            </div>
          </Providers>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
