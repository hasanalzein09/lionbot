import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/services/api_service.dart';

// Cart Item Model
class CartItem {
  final int menuItemId;
  final String name;
  final double price;
  final int quantity;
  final String? notes;

  CartItem({
    required this.menuItemId,
    required this.name,
    required this.price,
    required this.quantity,
    this.notes,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      menuItemId: json['menu_item_id'],
      name: json['name'] ?? '',
      price: (json['price'] ?? 0).toDouble(),
      quantity: json['quantity'] ?? 1,
      notes: json['notes'],
    );
  }

  CartItem copyWith({int? quantity}) {
    return CartItem(
      menuItemId: menuItemId,
      name: name,
      price: price,
      quantity: quantity ?? this.quantity,
      notes: notes,
    );
  }
}

// Cart State
class CartState {
  final int? restaurantId;
  final String? restaurantName;
  final List<CartItem> items;
  final bool isLoading;
  final String? error;

  CartState({
    this.restaurantId,
    this.restaurantName,
    this.items = const [],
    this.isLoading = false,
    this.error,
  });

  double get subtotal => items.fold(0, (sum, item) => sum + (item.price * item.quantity));
  double get deliveryFee => 2.0;
  double get total => subtotal + deliveryFee;
  int get itemCount => items.fold(0, (sum, item) => sum + item.quantity);
  bool get isEmpty => items.isEmpty;

  CartState copyWith({
    int? restaurantId,
    String? restaurantName,
    List<CartItem>? items,
    bool? isLoading,
    String? error,
  }) {
    return CartState(
      restaurantId: restaurantId ?? this.restaurantId,
      restaurantName: restaurantName ?? this.restaurantName,
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

// Cart Notifier
class CartNotifier extends StateNotifier<CartState> {
  CartNotifier() : super(CartState());

  final _api = ApiService();

  Future<void> loadCart() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final data = await _api.getCart();
      final items = (data['items'] as List?)
          ?.map((e) => CartItem.fromJson(e))
          .toList() ?? [];
      state = CartState(
        restaurantId: data['restaurant_id'],
        restaurantName: data['restaurant_name'],
        items: items,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> addItem(int menuItemId, int quantity, {String? notes}) async {
    state = state.copyWith(isLoading: true);
    try {
      await _api.addToCart(menuItemId, quantity, notes: notes);
      await loadCart();
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> updateQuantity(int menuItemId, int quantity) async {
    if (quantity <= 0) {
      await removeItem(menuItemId);
      return;
    }
    
    // Optimistic update
    final updatedItems = state.items.map((item) {
      if (item.menuItemId == menuItemId) {
        return item.copyWith(quantity: quantity);
      }
      return item;
    }).toList();
    state = state.copyWith(items: updatedItems);

    try {
      await _api.updateCartItem(menuItemId, quantity);
    } catch (e) {
      await loadCart(); // Revert on error
    }
  }

  Future<void> removeItem(int menuItemId) async {
    // Optimistic update
    final updatedItems = state.items.where((item) => item.menuItemId != menuItemId).toList();
    state = state.copyWith(items: updatedItems);

    try {
      await _api.removeFromCart(menuItemId);
      if (updatedItems.isEmpty) {
        state = CartState();
      }
    } catch (e) {
      await loadCart();
    }
  }

  Future<void> clearCart() async {
    state = state.copyWith(isLoading: true);
    try {
      await _api.clearCart();
      state = CartState();
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<Map<String, dynamic>?> checkout(String address, {String? notes}) async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _api.checkout(address, notes: notes);
      state = CartState(); // Clear cart after successful checkout
      return result;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return null;
    }
  }
}

// Providers
final cartProvider = StateNotifierProvider<CartNotifier, CartState>((ref) {
  return CartNotifier();
});
