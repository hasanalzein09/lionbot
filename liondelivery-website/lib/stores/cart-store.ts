import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface CartItemVariant {
  id: string;
  name: string;
  nameAr?: string;
  price: number;
}

export interface CartItemAddon {
  id: string;
  name: string;
  nameAr?: string;
  price: number;
  quantity: number;
}

export interface CartItem {
  id: string;
  productId: string;
  name: string;
  nameAr?: string;
  description?: string;
  image?: string;
  price: number;
  quantity: number;
  variant?: CartItemVariant;
  addons?: CartItemAddon[];
  notes?: string;
  restaurantId: string;
  restaurantName: string;
  restaurantNameAr?: string;
}

interface CartState {
  items: CartItem[];
  restaurantId: string | null;
  restaurantName: string | null;
  restaurantNameAr: string | null;
  notes: string;
  promoCode: string | null;
  discount: number;

  // Actions
  addItem: (item: Omit<CartItem, "id">) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, quantity: number) => void;
  updateNotes: (id: string, notes: string) => void;
  setOrderNotes: (notes: string) => void;
  setPromoCode: (code: string | null, discount?: number) => void;
  clearCart: () => void;

  // Getters
  getTotalItems: () => number;
  getSubtotal: () => number;
  getTotal: () => number;
  getDeliveryFee: () => number;
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      restaurantId: null,
      restaurantName: null,
      restaurantNameAr: null,
      notes: "",
      promoCode: null,
      discount: 0,

      addItem: (item) => {
        const state = get();

        // Check if adding from a different restaurant
        if (state.restaurantId && state.restaurantId !== item.restaurantId) {
          // Clear cart if different restaurant
          set({
            items: [],
            restaurantId: item.restaurantId,
            restaurantName: item.restaurantName,
            restaurantNameAr: item.restaurantNameAr,
            notes: "",
            promoCode: null,
            discount: 0,
          });
        }

        // Check if same item exists (same product, variant, and addons)
        const existingItemIndex = state.items.findIndex((i) => {
          if (i.productId !== item.productId) return false;
          if (i.variant?.id !== item.variant?.id) return false;
          if (i.notes !== item.notes) return false;

          // Compare addons
          const existingAddons = JSON.stringify(i.addons?.sort((a, b) => a.id.localeCompare(b.id)));
          const newAddons = JSON.stringify(item.addons?.sort((a, b) => a.id.localeCompare(b.id)));
          return existingAddons === newAddons;
        });

        if (existingItemIndex > -1) {
          // Update quantity of existing item
          const newItems = [...state.items];
          newItems[existingItemIndex].quantity += item.quantity;
          set({ items: newItems });
        } else {
          // Add new item
          set({
            items: [...state.items, { ...item, id: generateId() }],
            restaurantId: item.restaurantId,
            restaurantName: item.restaurantName,
            restaurantNameAr: item.restaurantNameAr,
          });
        }
      },

      removeItem: (id) => {
        const state = get();
        const newItems = state.items.filter((item) => item.id !== id);

        if (newItems.length === 0) {
          // Clear restaurant info if cart is empty
          set({
            items: [],
            restaurantId: null,
            restaurantName: null,
            restaurantNameAr: null,
            notes: "",
            promoCode: null,
            discount: 0,
          });
        } else {
          set({ items: newItems });
        }
      },

      updateQuantity: (id, quantity) => {
        if (quantity <= 0) {
          get().removeItem(id);
          return;
        }

        set({
          items: get().items.map((item) =>
            item.id === id ? { ...item, quantity } : item
          ),
        });
      },

      updateNotes: (id, notes) => {
        set({
          items: get().items.map((item) =>
            item.id === id ? { ...item, notes } : item
          ),
        });
      },

      setOrderNotes: (notes) => {
        set({ notes });
      },

      setPromoCode: (code, discount = 0) => {
        set({ promoCode: code, discount });
      },

      clearCart: () => {
        set({
          items: [],
          restaurantId: null,
          restaurantName: null,
          restaurantNameAr: null,
          notes: "",
          promoCode: null,
          discount: 0,
        });
      },

      getTotalItems: () => {
        return get().items.reduce((total, item) => total + item.quantity, 0);
      },

      getSubtotal: () => {
        return get().items.reduce((total, item) => {
          let itemTotal = item.price;

          // Add variant price
          if (item.variant) {
            itemTotal = item.variant.price;
          }

          // Add addons price
          if (item.addons) {
            itemTotal += item.addons.reduce(
              (sum, addon) => sum + addon.price * addon.quantity,
              0
            );
          }

          return total + itemTotal * item.quantity;
        }, 0);
      },

      getDeliveryFee: () => {
        // Fixed delivery fee for now
        return 2.0;
      },

      getTotal: () => {
        const state = get();
        const subtotal = state.getSubtotal();
        const deliveryFee = state.getDeliveryFee();
        const discount = state.discount;
        return Math.max(0, subtotal + deliveryFee - discount);
      },
    }),
    {
      name: "lion-delivery-cart",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        items: state.items,
        restaurantId: state.restaurantId,
        restaurantName: state.restaurantName,
        restaurantNameAr: state.restaurantNameAr,
        notes: state.notes,
        promoCode: state.promoCode,
        discount: state.discount,
      }),
    }
  )
);
