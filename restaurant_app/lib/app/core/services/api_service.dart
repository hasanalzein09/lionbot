import 'package:dio/dio.dart';
import 'package:get/get.dart' hide Response;
import '../constants/api_constants.dart';
import 'storage_service.dart';

class ApiService extends GetxService {
  late Dio _dio;
  final StorageService _storage = Get.find<StorageService>();

  @override
  void onInit() {
    super.onInit();
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Add auth interceptor
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          // Token expired - logout
          _storage.clearAll();
          Get.offAllNamed('/login');
        }
        return handler.next(error);
      },
    ));
  }

  // Auth
  Future<Response> login(String email, String password) async {
    return await _dio.post(
      ApiConstants.login,
      data: {
        'username': email,
        'password': password,
      },
      options: Options(contentType: 'application/x-www-form-urlencoded'),
    );
  }

  Future<Response> getMe() async {
    return await _dio.get(ApiConstants.me);
  }

  // Restaurants
  Future<Response> getRestaurants() async {
    return await _dio.get(ApiConstants.restaurants);
  }

  Future<Response> getRestaurant(int id) async {
    return await _dio.get('${ApiConstants.restaurants}/$id');
  }

  // Menus
  Future<Response> getMenus(int restaurantId) async {
    return await _dio.get('${ApiConstants.menus}?restaurant_id=$restaurantId');
  }

  Future<Response> createMenu(Map<String, dynamic> data) async {
    return await _dio.post(ApiConstants.menus, data: data);
  }

  Future<Response> updateMenu(int id, Map<String, dynamic> data) async {
    return await _dio.put('${ApiConstants.menus}/$id', data: data);
  }

  Future<Response> deleteMenu(int id) async {
    return await _dio.delete('${ApiConstants.menus}/$id');
  }

  // Categories
  Future<Response> getCategories(int menuId) async {
    return await _dio.get('${ApiConstants.categories}/', queryParameters: {'menu_id': menuId});
  }

  Future<Response> createCategory(Map<String, dynamic> data) async {
    return await _dio.post(ApiConstants.categories, data: data);
  }

  Future<Response> updateCategory(int id, Map<String, dynamic> data) async {
    return await _dio.put('${ApiConstants.categories}/$id', data: data);
  }

  Future<Response> deleteCategory(int id) async {
    return await _dio.delete('${ApiConstants.categories}/$id');
  }

  // Menu Items
  Future<Response> getMenuItems(int categoryId) async {
    return await _dio.get('${ApiConstants.menuItems}/', queryParameters: {'category_id': categoryId});
  }

  Future<Response> createMenuItem(Map<String, dynamic> data) async {
    return await _dio.post(ApiConstants.menuItems, data: data);
  }

  Future<Response> updateMenuItem(int id, Map<String, dynamic> data) async {
    return await _dio.put('${ApiConstants.menuItems}/$id', data: data);
  }

  Future<Response> deleteMenuItem(int id) async {
    return await _dio.delete('${ApiConstants.menuItems}/$id');
  }

  // Orders
  Future<Response> getOrders({int? restaurantId, String? status}) async {
    final params = <String, dynamic>{};
    if (restaurantId != null) params['restaurant_id'] = restaurantId;
    if (status != null) params['status'] = status;
    return await _dio.get(ApiConstants.orders, queryParameters: params);
  }

  Future<Response> getOrder(int id) async {
    return await _dio.get('${ApiConstants.orders}/$id');
  }

  Future<Response> updateOrderStatus(int id, String status) async {
    return await _dio.patch('${ApiConstants.orders}/$id/status', data: {'status': status});
  }

  // Stats
  Future<Response> getStats(int restaurantId) async {
    return await _dio.get('${ApiConstants.stats}/restaurant/$restaurantId');
  }
}
