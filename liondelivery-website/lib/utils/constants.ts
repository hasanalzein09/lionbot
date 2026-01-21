export const SITE_CONFIG = {
  name: "Lion Delivery",
  nameAr: "لايون ديليفري",
  description: "Order from the best restaurants in Saida",
  descriptionAr: "أطلب من أفضل مطاعم صيدا",
  url: "https://liondelivery-saida.com",
  ogImage: "/images/og-image.jpg",
  locale: "ar",
  locales: ["ar", "en"] as const,
  contact: {
    phone: process.env.NEXT_PUBLIC_WHATSAPP_NUMBER || "+96170000000",
    whatsapp: process.env.NEXT_PUBLIC_WHATSAPP_NUMBER || "+96170000000",
    email: "info@liondelivery-saida.com",
  },
  social: {
    facebook: "https://facebook.com/liondelivery",
    instagram: "https://instagram.com/liondelivery",
  },
};

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://lion.hmz.technology/api/v1";

export const WHATSAPP_NUMBER = process.env.NEXT_PUBLIC_WHATSAPP_NUMBER || "+961";

export const DELIVERY_FEE = 2.0; // USD

export const CURRENCY = {
  code: "USD",
  symbol: "$",
  locale: "en-US",
};

export const CATEGORIES_ICONS: Record<string, string> = {
  burger: "🍔",
  shawarma: "🥙",
  pizza: "🍕",
  coffee: "☕",
  salad: "🥗",
  dessert: "🍰",
  juice: "🥤",
  chicken: "🍗",
  seafood: "🐟",
  grill: "🔥",
  sandwich: "🥪",
  breakfast: "🍳",
  default: "🍽️",
};

export const ORDER_STATUS = {
  pending: { label: "قيد الانتظار", labelEn: "Pending", color: "yellow" },
  confirmed: { label: "تم التأكيد", labelEn: "Confirmed", color: "blue" },
  preparing: { label: "قيد التحضير", labelEn: "Preparing", color: "orange" },
  ready: { label: "جاهز", labelEn: "Ready", color: "green" },
  delivering: { label: "قيد التوصيل", labelEn: "Delivering", color: "purple" },
  delivered: { label: "تم التوصيل", labelEn: "Delivered", color: "green" },
  cancelled: { label: "ملغي", labelEn: "Cancelled", color: "red" },
} as const;

export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  "2xl": 1536,
} as const;
