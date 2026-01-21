import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/app_config.dart';

/// Custom exception for API errors
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic data;

  ApiException({required this.message, this.statusCode, this.data});

  @override
  String toString() => 'ApiException: $message (status: $statusCode)';
}

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal() {
    _init();
  }

  late Dio _dio;
  final _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  /// API Base URL from environment configuration
  /// Pass via: --dart-define=API_BASE_URL=https://your-api.com/api/v1
  static String get baseUrl => AppConfig.apiBaseUrl;

  /// Check if API is properly configured
  static bool get isConfigured => AppConfig.isConfigured;

  Dio get client => _dio;

  void _init() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: AppConfig.requestTimeoutSeconds),
      receiveTimeout: const Duration(seconds: AppConfig.requestTimeoutSeconds),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Add interceptors
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Add auth token
        final token = await _storage.read(key: 'token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }

        // Add trailing slash for collection endpoints (GET and POST)
        // Don't add for single resource endpoints (paths ending with ID like /orders/30)
        // Don't add for specific endpoints that don't need trailing slash
        final noSlashEndpoints = ['/login/access-token'];
        final needsSlash = !options.path.endsWith('/') &&
                          !options.path.contains('?') &&
                          !noSlashEndpoints.any((e) => options.path.contains(e));

        if (needsSlash && (options.method == 'GET' || options.method == 'POST')) {
          final lastSegment = options.path.split('/').last;
          final isResourceId = int.tryParse(lastSegment) != null;
          if (!isResourceId) {
            options.path = '${options.path}/';
          }
        }

        return handler.next(options);
      },
      onError: (error, handler) async {
        // Handle 401 - Token expired
        if (error.response?.statusCode == 401) {
          await _storage.delete(key: 'token');
          return handler.next(error);
        }

        // Retry logic for network errors and 5xx server errors
        final shouldRetry = error.type == DioExceptionType.connectionTimeout ||
            error.type == DioExceptionType.sendTimeout ||
            error.type == DioExceptionType.receiveTimeout ||
            error.type == DioExceptionType.connectionError ||
            (error.response?.statusCode != null && error.response!.statusCode! >= 500);

        if (shouldRetry) {
          final retryCount = error.requestOptions.extra['retryCount'] ?? 0;
          if (retryCount < 3) {
            // Wait before retrying with exponential backoff
            await Future.delayed(Duration(seconds: retryCount + 1));

            // Increment retry count
            error.requestOptions.extra['retryCount'] = retryCount + 1;

            // Retry the request
            try {
              final response = await _dio.fetch(error.requestOptions);
              return handler.resolve(response);
            } catch (e) {
              return handler.next(error);
            }
          }
        }

        return handler.next(error);
      },
    ));
  }

  // ==================== Auth ====================
  
  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await _dio.post(
      '/login/access-token',
      data: FormData.fromMap({
        'username': username,
        'password': password,
        'grant_type': 'password',
      }),
      options: Options(contentType: Headers.formUrlEncodedContentType),
    );
    return response.data;
  }

  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await _dio.get('/users/me');
    return response.data;
  }

  // ==================== Users Management ====================
  
  Future<List<dynamic>> getUsers({String? role}) async {
    final params = <String, dynamic>{};
    if (role != null) params['role'] = role;
    final response = await _dio.get('/users', queryParameters: params);
    return response.data;
  }

  Future<Map<String, dynamic>> getUser(int userId) async {
    final response = await _dio.get('/users/$userId');
    return response.data;
  }

  Future<Map<String, dynamic>> createUser(Map<String, dynamic> data) async {
    final response = await _dio.post('/users', data: data);
    return response.data;
  }

  Future<void> updateUser(int userId, Map<String, dynamic> data) async {
    await _dio.patch('/users/$userId', data: data);
  }

  Future<void> deleteUser(int userId) async {
    await _dio.delete('/users/$userId');
  }

  // ==================== Dashboard Stats ====================
  
  Future<Map<String, dynamic>> getDashboardStats() async {
    final response = await _dio.get('/stats/dashboard');
    return response.data;
  }

  // ==================== Orders ====================
  
  Future<List<dynamic>> getOrders({int skip = 0, int limit = 50, String? status}) async {
    final params = <String, dynamic>{'skip': skip, 'limit': limit};
    if (status != null) params['status'] = status;
    
    final response = await _dio.get('/orders', queryParameters: params);
    return response.data;
  }

  Future<Map<String, dynamic>> getOrder(int orderId) async {
    final response = await _dio.get('/orders/$orderId');
    return response.data;
  }

  Future<void> updateOrderStatus(int orderId, String status) async {
    await _dio.patch('/orders/$orderId/status', data: {'status': status});
  }

  Future<void> assignDriverToOrder(int orderId, int driverId) async {
    await _dio.post('/orders/$orderId/assign', data: {'driver_id': driverId});
  }

  Future<void> autoAssignDriver(int orderId) async {
    await _dio.post('/orders/$orderId/auto-assign');
  }

  // ==================== Restaurants ====================
  
  Future<List<dynamic>> getRestaurants() async {
    final response = await _dio.get('/restaurants');
    return response.data;
  }

  Future<Map<String, dynamic>> getRestaurant(int restaurantId) async {
    final response = await _dio.get('/restaurants/$restaurantId');
    return response.data;
  }

  Future<Map<String, dynamic>> createRestaurant(Map<String, dynamic> data) async {
    final response = await _dio.post('/restaurants', data: data);
    return response.data;
  }

  Future<void> updateRestaurant(int restaurantId, Map<String, dynamic> data) async {
    await _dio.put('/restaurants/$restaurantId', data: data);
  }

  Future<void> deleteRestaurant(int restaurantId) async {
    await _dio.delete('/restaurants/$restaurantId');
  }

  // ==================== Restaurant Categories ====================

  Future<List<dynamic>> getRestaurantCategories() async {
    final response = await _dio.get('/restaurants/categories');
    return response.data;
  }

  // ==================== Menu Management ====================

  Future<List<dynamic>> getMenus(int restaurantId) async {
    final response = await _dio.get('/menus/restaurant/$restaurantId');
    return response.data;
  }

  Future<Map<String, dynamic>> createMenu(Map<String, dynamic> data) async {
    final response = await _dio.post('/menus', data: data);
    return response.data;
  }

  Future<void> updateMenu(int menuId, Map<String, dynamic> data) async {
    await _dio.put('/menus/$menuId', data: data);
  }

  Future<void> deleteMenu(int menuId) async {
    await _dio.delete('/menus/$menuId');
  }

  // ==================== Menu Categories ====================

  Future<List<dynamic>> getMenuCategories({int? menuId}) async {
    final params = <String, dynamic>{};
    if (menuId != null) params['menu_id'] = menuId;
    final response = await _dio.get('/menus/categories', queryParameters: params);
    return response.data;
  }

  Future<Map<String, dynamic>> createMenuCategory(Map<String, dynamic> data) async {
    final response = await _dio.post('/menus/categories', data: data);
    return response.data;
  }

  Future<void> updateMenuCategory(int categoryId, Map<String, dynamic> data) async {
    await _dio.put('/menus/categories/$categoryId', data: data);
  }

  Future<void> deleteMenuCategory(int categoryId) async {
    await _dio.delete('/menus/categories/$categoryId');
  }

  // ==================== Menu Items ====================

  Future<List<dynamic>> getMenuItems({int? categoryId}) async {
    final params = <String, dynamic>{};
    if (categoryId != null) params['category_id'] = categoryId;
    final response = await _dio.get('/menus/items', queryParameters: params);
    return response.data;
  }

  Future<Map<String, dynamic>> getMenuItem(int itemId) async {
    final response = await _dio.get('/menus/items/$itemId');
    return response.data;
  }

  Future<Map<String, dynamic>> createMenuItem(Map<String, dynamic> data) async {
    final response = await _dio.post('/menus/items', data: data);
    return response.data;
  }

  Future<void> updateMenuItem(int itemId, Map<String, dynamic> data) async {
    await _dio.put('/menus/items/$itemId', data: data);
  }

  Future<void> deleteMenuItem(int itemId) async {
    await _dio.delete('/menus/items/$itemId');
  }

  // ==================== FCM Token ====================

  Future<void> registerFcmToken(String token) async {
    await _dio.post('/notifications/register-token', data: {'fcm_token': token});
  }

  Future<void> unregisterFcmToken() async {
    await _dio.post('/notifications/unregister-token');
  }

  // ==================== Drivers ====================
  
  Future<List<dynamic>> getDrivers() async {
    final response = await _dio.get('/users', queryParameters: {'role': 'driver'});
    return response.data;
  }

  Future<Map<String, dynamic>> getDriverStats(int driverId) async {
    final response = await _dio.get('/users/$driverId/driver-stats');
    return response.data;
  }

  Future<Map<String, dynamic>> getAssignmentStats() async {
    final response = await _dio.get('/drivers/assignment/stats');
    return response.data;
  }

  Future<List<dynamic>> getNearbyDrivers(double lat, double lng, {double radius = 5.0}) async {
    final response = await _dio.post('/drivers/assignment/nearby', data: {
      'latitude': lat,
      'longitude': lng,
      'radius_km': radius,
    });
    return response.data['drivers'];
  }

  // ==================== Inventory ====================
  
  Future<List<dynamic>> getInventory(int restaurantId) async {
    final response = await _dio.get('/inventory/$restaurantId/items');
    return response.data;
  }

  Future<List<dynamic>> getLowStockItems(int restaurantId) async {
    final response = await _dio.get('/inventory/$restaurantId/low-stock');
    return response.data;
  }

  Future<Map<String, dynamic>> getInventoryValue(int restaurantId) async {
    final response = await _dio.get('/inventory/$restaurantId/value');
    return response.data;
  }

  Future<void> addStock(int itemId, double quantity, double unitCost, {String? notes}) async {
    await _dio.post('/inventory/items/$itemId/add-stock', data: {
      'quantity': quantity,
      'unit_cost': unitCost,
      'notes': notes,
    });
  }

  Future<void> deductStock(int itemId, double quantity, String reason, {String? notes}) async {
    await _dio.post('/inventory/items/$itemId/deduct-stock', data: {
      'quantity': quantity,
      'reason': reason,
      'notes': notes,
    });
  }

  // ==================== Loyalty ====================
  
  Future<Map<String, dynamic>> getTierInfo() async {
    final response = await _dio.get('/loyalty/tiers');
    return response.data;
  }

  // ==================== Settings ====================

  Future<Map<String, dynamic>> getSettings() async {
    final response = await _dio.get('/settings');
    return response.data;
  }

  Future<void> updateSettings(Map<String, dynamic> settings) async {
    await _dio.put('/settings', data: settings);
  }

  // ==================== Customers ====================

  Future<List<dynamic>> getCustomers() async {
    final response = await _dio.get('/users', queryParameters: {'role': 'customer'});
    return response.data;
  }

  Future<List<dynamic>> getUserOrders(int userId) async {
    // Get all orders and filter by user_id on client side
    // Or if backend supports it: /orders?user_id=$userId
    final response = await _dio.get('/orders', queryParameters: {'limit': 100});
    final orders = response.data as List<dynamic>;
    return orders.where((o) => o['user_id'] == userId).toList();
  }

  // ==================== Addresses ====================

  Future<List<dynamic>> getUserAddresses(int userId) async {
    final response = await _dio.get('/addresses/user/$userId');
    return response.data;
  }

  Future<void> createUserAddress(int userId, Map<String, dynamic> data) async {
    await _dio.post('/addresses/user/$userId', data: data);
  }

  Future<void> updateAddress(int addressId, Map<String, dynamic> data) async {
    await _dio.put('/addresses/admin/$addressId', data: data);
  }

  Future<void> deleteAddress(int addressId) async {
    await _dio.delete('/addresses/admin/$addressId');
  }
}
