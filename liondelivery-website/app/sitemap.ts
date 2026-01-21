import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = "https://liondelivery-saida.com";

  // Static pages
  const staticPages = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: "daily" as const,
      priority: 1,
    },
    {
      url: `${baseUrl}/ar`,
      lastModified: new Date(),
      changeFrequency: "daily" as const,
      priority: 1,
    },
    {
      url: `${baseUrl}/en`,
      lastModified: new Date(),
      changeFrequency: "daily" as const,
      priority: 1,
    },
    {
      url: `${baseUrl}/ar/restaurants`,
      lastModified: new Date(),
      changeFrequency: "daily" as const,
      priority: 0.9,
    },
    {
      url: `${baseUrl}/en/restaurants`,
      lastModified: new Date(),
      changeFrequency: "daily" as const,
      priority: 0.9,
    },
    {
      url: `${baseUrl}/ar/search`,
      lastModified: new Date(),
      changeFrequency: "weekly" as const,
      priority: 0.7,
    },
    {
      url: `${baseUrl}/en/search`,
      lastModified: new Date(),
      changeFrequency: "weekly" as const,
      priority: 0.7,
    },
  ];

  // In production, fetch restaurants and generate URLs
  // const restaurants = await fetchRestaurants();
  // const restaurantPages = restaurants.flatMap((restaurant) => [
  //   {
  //     url: `${baseUrl}/ar/restaurants/${restaurant.slug}`,
  //     lastModified: new Date(restaurant.updatedAt),
  //     changeFrequency: "weekly" as const,
  //     priority: 0.8,
  //   },
  //   {
  //     url: `${baseUrl}/en/restaurants/${restaurant.slug}`,
  //     lastModified: new Date(restaurant.updatedAt),
  //     changeFrequency: "weekly" as const,
  //     priority: 0.8,
  //   },
  // ]);

  return staticPages;
}
