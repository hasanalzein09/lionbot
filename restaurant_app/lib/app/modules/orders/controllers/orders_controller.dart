import 'package:get/get.dart';
import '../../../core/services/api_service.dart';
import '../../../core/services/storage_service.dart';

class OrdersController extends GetxController with GetSingleTickerProviderStateMixin {
  final ApiService _api = Get.find<ApiService>();
  final StorageService _storage = Get.find<StorageService>();

  final isLoading = true.obs;
  final orders = <Map<String, dynamic>>[].obs;
  final selectedTab = 0.obs;

  final statusFilters = ['new', 'accepted', 'preparing', 'ready'];

  @override
  void onInit() {
    super.onInit();
    loadOrders();
  }

  Future<void> loadOrders() async {
    isLoading.value = true;
    try {
      final restaurantId = await _storage.getRestaurantId();
      final status = statusFilters[selectedTab.value];
      
      final response = await _api.getOrders(
        restaurantId: restaurantId,
        status: status,
      );
      
      if (response.statusCode == 200) {
        orders.value = List<Map<String, dynamic>>.from(response.data);
      }
    } catch (e) {
      print('Error loading orders: $e');
    } finally {
      isLoading.value = false;
    }
  }

  void changeTab(int index) {
    selectedTab.value = index;
    loadOrders();
  }

  Future<void> updateOrderStatus(int orderId, String newStatus) async {
    try {
      final response = await _api.updateOrderStatus(orderId, newStatus);
      if (response.statusCode == 200) {
        Get.snackbar('نجاح', 'تم تحديث حالة الطلب');
        loadOrders();
      }
    } catch (e) {
      Get.snackbar('خطأ', 'فشل تحديث حالة الطلب');
    }
  }

  String getStatusLabel(String status) {
    switch (status) {
      case 'new':
        return 'جديد';
      case 'accepted':
        return 'مقبول';
      case 'preparing':
        return 'قيد التحضير';
      case 'ready':
        return 'جاهز';
      case 'out_for_delivery':
        return 'في الطريق';
      case 'delivered':
        return 'تم التوصيل';
      case 'cancelled':
        return 'ملغي';
      default:
        return status;
    }
  }

  String getNextStatus(String currentStatus) {
    switch (currentStatus) {
      case 'new':
        return 'accepted';
      case 'accepted':
        return 'preparing';
      case 'preparing':
        return 'ready';
      case 'ready':
        return 'out_for_delivery';
      default:
        return currentStatus;
    }
  }
}
