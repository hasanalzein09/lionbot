import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:lionbot_mobile/app/data/services/api_service.dart';

class OrdersController extends GetxController {
  final _api = ApiService().client;
  var orders = [].obs;
  var isLoading = true.obs;

  @override
  void onInit() {
    super.onInit();
    fetchOrders();
  }

  Future<void> fetchOrders() async {
    try {
      isLoading.value = true;
      final response = await _api.get('/orders/');
      orders.value = response.data;
    } catch (e) {
      Get.snackbar('Error', 'Failed to fetch orders');
    } finally {
      isLoading.value = false;
    }
  }
}

class OrdersView extends StatelessWidget {
  final OrdersController controller = Get.put(OrdersController());

  OrdersView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Live Orders'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: controller.fetchOrders,
          ),
        ],
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }
        
        if (controller.orders.isEmpty) {
          return const Center(child: Text('No orders found'));
        }

        return ListView.builder(
          itemCount: controller.orders.length,
          itemBuilder: (context, index) {
            final order = controller.orders[index];
            return Card(
              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: Colors.indigo[100],
                  child: Text('#${order['id']}'),
                ),
                title: Text('Total: \$${order['total_amount']}'),
                subtitle: Text('Status: ${order['status']}'),
                trailing: const Icon(Icons.chevron_right),
              ),
            );
          },
        );
      }),
    );
  }
}
