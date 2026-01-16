import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/services/api_service.dart';

// Order Model
class CustomerOrder {
  final int id;
  final String status;
  final double totalAmount;
  final String? restaurantName;
  final int? restaurantId;
  final DateTime? createdAt;
  final String? deliveryAddress;
  final List<dynamic>? items;

  CustomerOrder({
    required this.id,
    required this.status,
    required this.totalAmount,
    this.restaurantName,
    this.restaurantId,
    this.createdAt,
    this.deliveryAddress,
    this.items,
  });

  factory CustomerOrder.fromJson(Map<String, dynamic> json) {
    return CustomerOrder(
      id: json['id'],
      status: json['status'] ?? 'pending',
      totalAmount: (json['total_amount'] ?? 0).toDouble(),
      restaurantName: json['restaurant_name'],
      restaurantId: json['restaurant_id'],
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      deliveryAddress: json['delivery_address'],
      items: json['items'],
    );
  }
}

// Orders State
class OrdersState {
  final List<CustomerOrder> orders;
  final bool isLoading;
  final String? error;

  OrdersState({
    this.orders = const [],
    this.isLoading = false,
    this.error,
  });

  OrdersState copyWith({
    List<CustomerOrder>? orders,
    bool? isLoading,
    String? error,
  }) {
    return OrdersState(
      orders: orders ?? this.orders,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

// Orders Notifier
class OrdersNotifier extends StateNotifier<OrdersState> {
  OrdersNotifier() : super(OrdersState());

  final _api = ApiService();

  Future<void> loadOrders() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final data = await _api.getMyOrders();
      final orders = (data).map((e) => CustomerOrder.fromJson(e)).toList();
      state = OrdersState(orders: orders, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<CustomerOrder?> getOrderDetails(int orderId) async {
    try {
      final data = await _api.getOrder(orderId);
      return CustomerOrder.fromJson(data);
    } catch (e) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> trackOrder(int orderId) async {
    try {
      return await _api.trackOrder(orderId);
    } catch (e) {
      return null;
    }
  }
}

// Provider
final ordersProvider = StateNotifierProvider<OrdersNotifier, OrdersState>((ref) {
  return OrdersNotifier();
});
