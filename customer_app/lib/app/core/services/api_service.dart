import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal() { _init(); }

  late Dio _dio;
  final _storage = const FlutterSecureStorage();
  
  static const String baseUrl = 'https://lionbot-backend-426202982674.me-west1.run.app/api/v1';

  Dio get client => _dio;

  void _init() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: 'token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        if (!options.path.endsWith('/') && !options.path.contains('?')) {
          options.path = '${options.path}/';
        }
        return handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          await _storage.delete(key: 'token');
        }
        return handler.next(error);
      },
    ));
  }

  // ==================== Auth ====================
  
  Future<Map<String, dynamic>> login(String phone, String password) async {
    final response = await _dio.post('/login/access-token',
      data: FormData.fromMap({'username': phone, 'password': password, 'grant_type': 'password'}),
      options: Options(contentType: Headers.formUrlEncodedContentType),
    );
    return response.data;
  }

  Future<Map<String, dynamic>> register(String name, String phone, String password) async {
    final response = await _dio.post('/customers/register', data: {
      'full_name': name, 'phone_number': phone, 'password': password,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await _dio.get('/users/me');
    return response.data;
  }

  // ==================== Restaurants ====================
  
  Future<List<dynamic>> getRestaurants({String? category, bool? isOpen}) async {
    final params = <String, dynamic>{};
    if (category != null) params['category'] = category;
    if (isOpen != null) params['is_open'] = isOpen;
    final response = await _dio.get('/restaurants', queryParameters: params);
    return response.data;
  }

  Future<Map<String, dynamic>> getRestaurant(int id) async {
    final response = await _dio.get('/restaurants/$id');
    return response.data;
  }

  Future<List<dynamic>> getRestaurantMenu(int restaurantId) async {
    final response = await _dio.get('/menus', queryParameters: {'restaurant_id': restaurantId});
    return response.data;
  }

  // ==================== Cart ====================
  
  Future<Map<String, dynamic>> getCart() async {
    final response = await _dio.get('/cart');
    return response.data;
  }

  Future<void> addToCart(int menuItemId, int quantity, {String? notes}) async {
    await _dio.post('/cart/items', data: {
      'menu_item_id': menuItemId, 'quantity': quantity, 'notes': notes,
    });
  }

  Future<void> updateCartItem(int menuItemId, int quantity) async {
    await _dio.put('/cart/items/$menuItemId', data: {'quantity': quantity});
  }

  Future<void> removeFromCart(int menuItemId) async {
    await _dio.delete('/cart/items/$menuItemId');
  }

  Future<void> clearCart() async {
    await _dio.delete('/cart');
  }

  Future<Map<String, dynamic>> checkout(String address, {String? notes}) async {
    final response = await _dio.post('/cart/checkout', queryParameters: {
      'delivery_address': address, 'notes': notes,
    });
    return response.data;
  }

  // ==================== Orders ====================
  
  Future<List<dynamic>> getMyOrders() async {
    final response = await _dio.get('/customers/my-orders');
    return response.data;
  }

  Future<Map<String, dynamic>> getOrder(int orderId) async {
    final response = await _dio.get('/customers/my-orders/$orderId');
    return response.data;
  }

  Future<Map<String, dynamic>> trackOrder(int orderId) async {
    final response = await _dio.get('/customers/my-orders/$orderId/track');
    return response.data;
  }

  // ==================== Loyalty ====================
  
  Future<Map<String, dynamic>> getLoyaltyStatus() async {
    final response = await _dio.get('/loyalty/status');
    return response.data;
  }

  Future<List<dynamic>> getAvailableRewards() async {
    final response = await _dio.get('/loyalty/rewards');
    return response.data;
  }

  Future<Map<String, dynamic>> redeemReward(int rewardId) async {
    final response = await _dio.post('/loyalty/redeem', data: {'reward_id': rewardId});
    return response.data;
  }
}

