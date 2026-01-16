import 'package:get/get.dart';
import '../../../core/services/api_service.dart';
import '../../../core/services/storage_service.dart';
import '../../../routes/app_pages.dart';

class DashboardController extends GetxController {
  final ApiService _api = Get.find<ApiService>();
  final StorageService _storage = Get.find<StorageService>();

  final currentIndex = 0.obs;
  final isLoading = true.obs;
  
  // Stats
  final todayOrders = 0.obs;
  final pendingOrders = 0.obs;
  final totalRevenue = 0.0.obs;
  final menuItemsCount = 0.obs;
  
  // User data
  final restaurantName = ''.obs;
  final userName = ''.obs;

  @override
  void onInit() {
    super.onInit();
    loadData();
  }

  Future<void> loadData() async {
    isLoading.value = true;
    try {
      final userData = await _storage.getUserData();
      if (userData != null) {
        userName.value = userData['full_name'] ?? '';
      }
      
      final restaurantId = await _storage.getRestaurantId();
      if (restaurantId != null) {
        await loadStats(restaurantId);
      }
    } catch (e) {
      print('Error loading dashboard data: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> loadStats(int restaurantId) async {
    try {
      final response = await _api.getStats(restaurantId);
      if (response.statusCode == 200) {
        final data = response.data;
        todayOrders.value = data['today_orders'] ?? 0;
        pendingOrders.value = data['pending_orders'] ?? 0;
        totalRevenue.value = (data['total_revenue'] ?? 0).toDouble();
        menuItemsCount.value = data['menu_items_count'] ?? 0;
        restaurantName.value = data['restaurant_name'] ?? 'مطعمي';
      }
    } catch (e) {
      print('Error loading stats: $e');
    }
  }

  void changeTab(int index) {
    currentIndex.value = index;
  }

  Future<void> logout() async {
    await _storage.clearAll();
    Get.offAllNamed(Routes.login);
  }
}
