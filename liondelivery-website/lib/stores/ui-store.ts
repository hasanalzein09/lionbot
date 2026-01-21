import { create } from "zustand";

interface UIState {
  // Modals
  isSearchOpen: boolean;
  isCartOpen: boolean;
  isMobileNavOpen: boolean;
  isMenuItemModalOpen: boolean;
  selectedMenuItemId: string | null;

  // Actions
  openSearch: () => void;
  closeSearch: () => void;
  toggleSearch: () => void;

  openCart: () => void;
  closeCart: () => void;
  toggleCart: () => void;

  openMobileNav: () => void;
  closeMobileNav: () => void;
  toggleMobileNav: () => void;

  openMenuItemModal: (itemId: string) => void;
  closeMenuItemModal: () => void;

  closeAll: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  // Initial state
  isSearchOpen: false,
  isCartOpen: false,
  isMobileNavOpen: false,
  isMenuItemModalOpen: false,
  selectedMenuItemId: null,

  // Search actions
  openSearch: () => set({ isSearchOpen: true }),
  closeSearch: () => set({ isSearchOpen: false }),
  toggleSearch: () => set((state) => ({ isSearchOpen: !state.isSearchOpen })),

  // Cart actions
  openCart: () => set({ isCartOpen: true }),
  closeCart: () => set({ isCartOpen: false }),
  toggleCart: () => set((state) => ({ isCartOpen: !state.isCartOpen })),

  // Mobile nav actions
  openMobileNav: () => set({ isMobileNavOpen: true }),
  closeMobileNav: () => set({ isMobileNavOpen: false }),
  toggleMobileNav: () =>
    set((state) => ({ isMobileNavOpen: !state.isMobileNavOpen })),

  // Menu item modal actions
  openMenuItemModal: (itemId) =>
    set({ isMenuItemModalOpen: true, selectedMenuItemId: itemId }),
  closeMenuItemModal: () =>
    set({ isMenuItemModalOpen: false, selectedMenuItemId: null }),

  // Close all
  closeAll: () =>
    set({
      isSearchOpen: false,
      isCartOpen: false,
      isMobileNavOpen: false,
      isMenuItemModalOpen: false,
      selectedMenuItemId: null,
    }),
}));
