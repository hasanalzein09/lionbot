import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/api/", "/cart", "/checkout", "/orders"],
    },
    sitemap: "https://liondelivery-saida.com/sitemap.xml",
  };
}
