import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/services/api_service.dart';
import '../core/services/cache_service.dart';

/// Order state
class OrdersState {
  final List<dynamic> orders;
  final bool isLoading;
  final String? error;
  final String? statusFilter;

  const OrdersState({
    this.orders = const [],
    this.isLoading = false,
    this.error,
    this.statusFilter,
  });

  OrdersState copyWith({
    List<dynamic>? orders,
    bool? isLoading,
    String? error,
    String? statusFilter,
  }) {
    return OrdersState(
      orders: orders ?? this.orders,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      statusFilter: statusFilter ?? this.statusFilter,
    );
  }

  /// Get orders filtered by status
  List<dynamic> get pendingOrders =>
      orders.where((o) => o['status'] == 'pending').toList();

  List<dynamic> get preparingOrders =>
      orders.where((o) => o['status'] == 'preparing').toList();

  List<dynamic> get deliveryOrders =>
      orders.where((o) => o['status'] == 'out_for_delivery').toList();

  List<dynamic> get completedOrders =>
      orders.where((o) => o['status'] == 'delivered').toList();

  int get pendingCount => pendingOrders.length;
}

/// Orders notifier
class OrdersNotifier extends StateNotifier<OrdersState> {
  final ApiService _api;
  final CacheService _cache;

  OrdersNotifier(this._api, this._cache) : super(const OrdersState());

  /// Load orders from API or cache
  Future<void> loadOrders({String? status, bool forceRefresh = false}) async {
    final cacheKey = CacheKeys.orders(status);

    // Try cache first if not forcing refresh
    if (!forceRefresh) {
      final cached = _cache.get<List<dynamic>>(cacheKey);
      if (cached != null) {
        state = state.copyWith(orders: cached, statusFilter: status);
        return;
      }
    }

    state = state.copyWith(isLoading: true, error: null);

    try {
      final orders = await _api.getOrders(status: status);
      _cache.set(cacheKey, orders, ttl: const Duration(minutes: 2));
      state = state.copyWith(
        orders: orders,
        isLoading: false,
        statusFilter: status,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load orders: ${e.toString()}',
      );
    }
  }

  /// Refresh orders
  Future<void> refresh() async {
    await loadOrders(status: state.statusFilter, forceRefresh: true);
  }

  /// Update order status
  Future<bool> updateOrderStatus(int orderId, String newStatus) async {
    try {
      await _api.updateOrderStatus(orderId, newStatus);
      // Invalidate cache and refresh
      _cache.removePrefix('orders_');
      await refresh();
      return true;
    } catch (e) {
      state = state.copyWith(error: 'Failed to update order status');
      return false;
    }
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(error: null);
  }
}

/// Provider for orders
final ordersProvider = StateNotifierProvider<OrdersNotifier, OrdersState>((ref) {
  return OrdersNotifier(ApiService(), CacheService());
});

/// Provider for pending orders count (for badges)
final pendingOrdersCountProvider = Provider<int>((ref) {
  return ref.watch(ordersProvider).pendingCount;
});
