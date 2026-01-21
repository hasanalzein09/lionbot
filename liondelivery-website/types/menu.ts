export interface MenuItem {
  id: string;
  name: string;
  nameAr?: string;
  description?: string;
  descriptionAr?: string;
  image?: string;
  price: number;
  originalPrice?: number;
  categoryId: string;
  categoryName?: string;
  categoryNameAr?: string;
  restaurantId: string;
  isAvailable?: boolean;
  isPopular?: boolean;
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
  id: string;
  name: string;
  nameAr?: string;
  price: number;
  isDefault?: boolean;
}

export interface MenuItemAddon {
  id: string;
  name: string;
  nameAr?: string;
  price: number;
  maxQuantity?: number;
  isRequired?: boolean;
}

export interface MenuCategory {
  id: string;
  name: string;
  nameAr?: string;
  description?: string;
  descriptionAr?: string;
  image?: string;
  sortOrder?: number;
  itemCount?: number;
  items?: MenuItem[];
}

export interface Menu {
  restaurantId: string;
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
