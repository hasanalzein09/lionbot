import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lionbot_mobile/app/data/services/driver_api_service.dart';
import 'package:lionbot_mobile/app/data/services/websocket_service.dart';
import 'package:lionbot_mobile/app/data/services/local_storage_service.dart';

/// Order model for type safety
class OrderModel {
  final int id;
  final String status;
  final double totalAmount;
  final String? deliveryAddress;
  final double? deliveryLatitude;
  final double? deliveryLongitude;
  final String? restaurantName;
  final String? customerPhone;
  final DateTime createdAt;

  OrderModel({
    required this.id,
    required this.status,
    required this.totalAmount,
    this.deliveryAddress,
    this.deliveryLatitude,
    this.deliveryLongitude,
    this.restaurantName,
    this.customerPhone,
    required this.createdAt,
  });

  factory OrderModel.fromJson(Map<String, dynamic> json) {
    return OrderModel(
      id: json['id'] as int,
      status: json['status'] as String,
      totalAmount: (json['total_amount'] as num).toDouble(),
      deliveryAddress: json['delivery_address'] as String?,
      deliveryLatitude: (json['delivery_latitude'] as num?)?.toDouble(),
      deliveryLongitude: (json['delivery_longitude'] as num?)?.toDouble(),
      restaurantName: json['restaurant_name'] as String?,
      customerPhone: json['customer_phone'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'status': status,
    'total_amount': totalAmount,
    'delivery_address': deliveryAddress,
    'delivery_latitude': deliveryLatitude,
    'delivery_longitude': deliveryLongitude,
    'restaurant_name': restaurantName,
    'customer_phone': customerPhone,
    'created_at': createdAt.toIso8601String(),
  };

  OrderModel copyWith({String? status}) {
    return OrderModel(
      id: id,
      status: status ?? this.status,
      totalAmount: totalAmount,
      deliveryAddress: deliveryAddress,
      deliveryLatitude: deliveryLatitude,
      deliveryLongitude: deliveryLongitude,
      restaurantName: restaurantName,
      customerPhone: customerPhone,
      createdAt: createdAt,
    );
  }
}

/// State class for orders
class OrdersState {
  final List<OrderModel> availableOrders;
  final List<OrderModel> myOrders;
  final bool isLoading;
  final String? error;

  OrdersState({
    this.availableOrders = const [],
    this.myOrders = const [],
    this.isLoading = false,
    this.error,
  });

  OrdersState copyWith({
    List<OrderModel>? availableOrders,
    List<OrderModel>? myOrders,
    bool? isLoading,
    String? error,
  }) {
    return OrdersState(
      availableOrders: availableOrders ?? this.availableOrders,
      myOrders: myOrders ?? this.myOrders,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// Orders Notifier with optimistic updates
class OrdersNotifier extends StateNotifier<OrdersState> {
  final DriverApiService _api;
  final WebSocketService _ws;
  final LocalStorageService _localStorage;
  final int? _driverId;

  OrdersNotifier(this._api, this._ws, this._localStorage, this._driverId) 
      : super(OrdersState()) {
    _init();
  }

  void _init() {
    // Load cached orders first (offline-first)
    final cached = _localStorage.getCachedOrders();
    if (cached.isNotEmpty) {
      state = state.copyWith(
        myOrders: cached.map((e) => OrderModel.fromJson(e)).toList(),
      );
    }
    
    // Then fetch fresh data
    refresh();
    
    // Listen to real-time updates
    _ws.messages.listen(_handleWebSocketMessage);
    
    // Connect to WebSocket if driver
    if (_driverId != null) {
      _ws.connectAsDriver(_driverId);
    }
  }

  void _handleWebSocketMessage(Map<String, dynamic> message) {
    switch (message['type']) {
      case 'new_order':
        // Add new order to available orders
        final order = OrderModel.fromJson(message['data']);
        state = state.copyWith(
          availableOrders: [order, ...state.availableOrders],
        );
        break;
        
      case 'order_update':
        // Update existing order
        final orderId = message['order_id'] as int;
        final newStatus = message['status'] as String;
        
        state = state.copyWith(
          myOrders: state.myOrders.map((o) {
            if (o.id == orderId) return o.copyWith(status: newStatus);
            return o;
          }).toList(),
        );
        break;
    }
  }

  Future<void> refresh() async {
    if (_driverId == null) return;
    
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final orders = await _api.getMyDeliveries(_driverId);
      final orderModels = (orders)
          .map((e) => OrderModel.fromJson(e as Map<String, dynamic>))
          .toList();
      
      state = state.copyWith(
        myOrders: orderModels,
        isLoading: false,
      );
      
      // Cache for offline
      await _localStorage.cacheOrders(
        orderModels.map((e) => e.toJson()).toList(),
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Accept order with optimistic update
  Future<void> acceptOrder(int orderId) async {
    // Optimistic update - immediately move to my orders
    final order = state.availableOrders.firstWhere((o) => o.id == orderId);
    final updatedOrder = order.copyWith(status: 'out_for_delivery');
    
    state = state.copyWith(
      availableOrders: state.availableOrders.where((o) => o.id != orderId).toList(),
      myOrders: [updatedOrder, ...state.myOrders],
    );
    
    try {
      await _api.updateOrderStatus(orderId, 'out_for_delivery');
    } catch (e) {
      // Rollback on failure
      state = state.copyWith(
        availableOrders: [order, ...state.availableOrders],
        myOrders: state.myOrders.where((o) => o.id != orderId).toList(),
        error: 'Failed to accept order',
      );
    }
  }

  /// Mark as delivered with optimistic update
  Future<void> markDelivered(int orderId) async {
    final order = state.myOrders.firstWhere((o) => o.id == orderId);
    final updatedOrder = order.copyWith(status: 'delivered');
    
    state = state.copyWith(
      myOrders: state.myOrders.map((o) {
        if (o.id == orderId) return updatedOrder;
        return o;
      }).toList(),
    );
    
    try {
      await _api.updateOrderStatus(orderId, 'delivered');
    } catch (e) {
      // Rollback
      state = state.copyWith(
        myOrders: state.myOrders.map((o) {
          if (o.id == orderId) return order;
          return o;
        }).toList(),
        error: 'Failed to update order',
      );
    }
  }
}

/// Main orders provider
final ordersProvider = StateNotifierProvider<OrdersNotifier, OrdersState>((ref) {
  final api = DriverApiService();
  final ws = ref.watch(webSocketServiceProvider);
  final localStorage = ref.watch(localStorageProvider);
  // TODO: Get driver ID from auth state
  const driverId = 1; // Placeholder
  
  return OrdersNotifier(api, ws, localStorage, driverId);
});
