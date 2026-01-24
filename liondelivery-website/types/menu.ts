export interface MenuItem {
  id: string | number;
  name: string;
  nameAr?: string;
  name_ar?: string; // API format
  description?: string;
  descriptionAr?: string;
  description_ar?: string; // API format
  image?: string;
  price?: number | null;
  price_min?: number | null; // API format
  price_max?: number | null; // API format
  originalPrice?: number;
  categoryId?: string | number;
  category_id?: string | number; // API format
  categoryName?: string;
  categoryNameAr?: string;
  restaurantId?: string | number;
  restaurant_id?: string | number; // API format
  isAvailable?: boolean;
  is_available?: boolean; // API format
  isPopular?: boolean;
  is_popular?: boolean; // API format
  hasVariants?: boolean;
  has_variants?: boolean; // API format
  variants?: MenuItemVariant[];
  addons?: MenuItemAddon[];
  tags?: string[];
  allergens?: string[];
  preparationTime?: number;
  calories?: number;
  createdAt?: string;
  updatedAt?: string;
}

export interface MenuItemVariant {
  id: string | number;
  name: string;
  nameAr?: string;
  name_ar?: string; // API format
  price: number;
  isDefault?: boolean;
}

export interface MenuItemAddon {
  id: string | number;
  name: string;
  nameAr?: string;
  name_ar?: string; // API format
  price: number;
  maxQuantity?: number;
  isRequired?: boolean;
}

export interface MenuCategory {
  id: string | number;
  name: string;
  nameAr?: string;
  name_ar?: string; // API format
  description?: string;
  descriptionAr?: string;
  description_ar?: string; // API format
  image?: string;
  sortOrder?: number;
  order?: number; // API format
  itemCount?: number;
  items?: MenuItem[];
}

export interface Menu {
  restaurantId: string | number;
  restaurant_id?: string | number; // API format
  categories: MenuCategory[];
}

export interface MenuResponse {
  menu: Menu;
  restaurant: {
    id: string;
    name: string;
    nameAr?: string;
  };
}
