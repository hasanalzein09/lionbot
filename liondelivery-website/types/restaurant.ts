export interface Restaurant {
  id: string | number;
  name: string;
  nameAr?: string;
  name_ar?: string; // API format
  slug: string;
  description?: string;
  descriptionAr?: string;
  description_ar?: string; // API format
  image?: string;
  coverImage?: string;
  cover_image?: string; // API format
  logo?: string;
  category?: string;
  categoryAr?: string;
  category_ar?: string; // API format
  category_id?: number;
  categories?: string[];
  rating?: number;
  reviewCount?: number;
  review_count?: number; // API format
  priceRange?: "$" | "$$" | "$$$" | "$$$$";
  deliveryTime?: {
    min: number;
    max: number;
  };
  delivery_time?: {
    min: number;
    max: number;
  }; // API format
  deliveryFee?: number;
  delivery_fee?: number; // API format
  minimumOrder?: number;
  isOpen?: boolean;
  is_open?: boolean; // API format
  isFeatured?: boolean;
  is_featured?: boolean; // API format
  workingHours?: WorkingHours;
  working_hours?: WorkingHours; // API format
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
