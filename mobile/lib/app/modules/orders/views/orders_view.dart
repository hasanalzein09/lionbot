import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:lionbot_mobile/app/data/services/api_service.dart';

import 'package:lionbot_mobile/app/data/services/driver_api_service.dart';
import 'package:lionbot_mobile/app/modules/login/controllers/auth_controller.dart';

class OrdersController extends GetxController {
  final _driverApi = DriverApiService();
  final _authController = Get.find<AuthController>();
  
  var availableOrders = [].obs;
  var myOrders = [].obs;
  var isLoading = true.obs;

  @override
  void onInit() {
    super.onInit();
    refreshData();
  }

  Future<void> refreshData() async {
    isLoading.value = true;
    await Future.wait([
      fetchAvailableOrders(),
      fetchMyOrders(),
    ]);
    isLoading.value = false;
  }

  Future<void> fetchAvailableOrders() async {
    try {
      // For now, reuse /orders/ with status ready/accepted
      // Better: Create /orders/available for drivers
      final response = await _driverApi.getMyDeliveries(0); // Dummy for test or refine
      availableOrders.value = response;
    } catch (e) {
      print('Error fetching available orders: $e');
    }
  }

  Future<void> fetchMyOrders() async {
    final driverId = _authController.currentUser['id'];
    if (driverId == null) return;
    try {
      final response = await _driverApi.getMyDeliveries(driverId);
      myOrders.value = response;
    } catch (e) {
      print('Error fetching my orders: $e');
    }
  }

  Future<void> acceptOrder(int orderId) async {
    try {
      await _driverApi.updateOrderStatus(orderId, 'out_for_delivery');
      Get.snackbar('Success', 'Order accepted');
      refreshData();
    } catch (e) {
      Get.snackbar('Error', 'Failed to accept order');
    }
  }
}

class OrdersView extends StatelessWidget {
  final OrdersController controller = Get.put(OrdersController());

  OrdersView({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        backgroundColor: Colors.grey[100],
        appBar: AppBar(
          title: const Text('Driver Dashboard', style: TextStyle(fontWeight: FontWeight.bold)),
          backgroundColor: Colors.white,
          foregroundColor: Colors.black,
          elevation: 0,
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Available'),
              Tab(text: 'My Deliveries'),
            ],
            labelColor: Colors.amber,
            unselectedLabelColor: Colors.grey,
            indicatorColor: Colors.amber,
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: controller.refreshData,
            ),
          ],
        ),
        body: TabBarView(
          children: [
            _buildOrdersList(controller.availableOrders, true),
            _buildOrdersList(controller.myOrders, false),
          ],
        ),
      ),
    );
  }

  Widget _buildOrdersList(RxList orders, bool isAvailable) {
    return Obx(() {
      if (controller.isLoading.value) {
        return const Center(child: CircularProgressIndicator(color: Colors.amber));
      }
      
      if (orders.isEmpty) {
        return Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.inventory_2_outlined, size: 64, color: Colors.grey[300]),
              const SizedBox(height: 16),
              const Text('No orders found', style: TextStyle(color: Colors.grey)),
            ],
          ),
        );
      }

      return ListView.builder(
        padding: const EdgeInsets.symmetric(vertical: 12),
        itemCount: orders.length,
        itemBuilder: (context, index) {
          final order = orders[index];
          return Container(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.between,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.receipt_long, color: Colors.amber),
                          const SizedBox(width: 8),
                          Text(
                            'Order #${order['id']}',
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                        decoration: BoxDecoration(
                          color: _getStatusColor(order['status']).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          order['status'].toUpperCase(),
                          style: TextStyle(
                            color: _getStatusColor(order['status']),
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const Divider(height: 24),
                  Row(
                    children: [
                      const Icon(Icons.location_on, color: Colors.redAccent, size: 18),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          order['delivery_address'] ?? 'Unknown Address',
                          style: TextStyle(color: Colors.grey[600]),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.between,
                    children: [
                      Text(
                        '\$${order['total_amount']}',
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      if (isAvailable)
                        ElevatedButton(
                          onPressed: () => controller.acceptOrder(order['id']),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.amber,
                            foregroundColor: Colors.black,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: const Text('ACCEPT'),
                        )
                      else
                        OutlinedButton(
                          onPressed: () => Get.toNamed('/order-details', arguments: order),
                          style: OutlinedButton.styleFrom(
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          child: const Text('DETAILS'),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          );
        },
      );
    });
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'pending': return Colors.orange;
      case 'out_for_delivery': return Colors.blue;
      case 'delivered': return Colors.green;
      default: return Colors.grey;
    }
  }
}
