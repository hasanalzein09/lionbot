export interface Restaurant {
  id: string;
  name: string;
  nameAr?: string;
  slug: string;
  description?: string;
  descriptionAr?: string;
  image?: string;
  coverImage?: string;
  logo?: string;
  category: string;
  categoryAr?: string;
  categories?: string[];
  rating?: number;
  reviewCount?: number;
  priceRange?: "$" | "$$" | "$$$" | "$$$$";
  deliveryTime?: {
    min: number;
    max: number;
  };
  deliveryFee?: number;
  minimumOrder?: number;
  isOpen?: boolean;
  isFeatured?: boolean;
  workingHours?: WorkingHours;
  address?: string;
  phone?: string;
  location?: {
    lat: number;
    lng: number;
  };
  createdAt?: string;
  updatedAt?: string;
}

export interface WorkingHours {
  monday?: DayHours;
  tuesday?: DayHours;
  wednesday?: DayHours;
  thursday?: DayHours;
  friday?: DayHours;
  saturday?: DayHours;
  sunday?: DayHours;
}

export interface DayHours {
  open: string;
  close: string;
  isClosed?: boolean;
}

export interface RestaurantListResponse {
  restaurants: Restaurant[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

export interface RestaurantFilters {
  category?: string;
  search?: string;
  sortBy?: "newest" | "rating" | "popular";
  page?: number;
  limit?: number;
}
