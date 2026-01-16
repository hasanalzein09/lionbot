import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../controllers/orders_controller.dart';

class OrdersView extends GetView<OrdersController> {
  const OrdersView({super.key});

  @override
  Widget build(BuildContext context) {
    // Register controller if not exists
    if (!Get.isRegistered<OrdersController>()) {
      Get.put(OrdersController());
    }
    
    return DefaultTabController(
      length: 4,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('الطلبات'),
          automaticallyImplyLeading: false,
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: controller.loadOrders,
            ),
          ],
          bottom: TabBar(
            onTap: controller.changeTab,
            tabs: const [
              Tab(text: 'جديدة'),
              Tab(text: 'مقبولة'),
              Tab(text: 'تحضير'),
              Tab(text: 'جاهزة'),
            ],
          ),
        ),
        body: Obx(() {
          if (controller.isLoading.value) {
            return const Center(child: CircularProgressIndicator());
          }

          if (controller.orders.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.receipt_long, size: 64, color: Colors.grey[300]),
                  const SizedBox(height: 16),
                  Text(
                    'لا توجد طلبات',
                    style: TextStyle(color: Colors.grey[500], fontSize: 18),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: controller.loadOrders,
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: controller.orders.length,
              itemBuilder: (context, index) {
                final order = controller.orders[index];
                return _buildOrderCard(context, order);
              },
            ),
          );
        }),
      ),
    );
  }

  Widget _buildOrderCard(BuildContext context, Map<String, dynamic> order) {
    final status = order['status'] ?? 'new';
    final items = order['items'] as List<dynamic>? ?? [];
    
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'طلب #${order['id']}',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                _buildStatusChip(status),
              ],
            ),
            
            const Divider(height: 24),
            
            // Items
            ...items.map((item) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  Text('${item['quantity']}x ', 
                    style: const TextStyle(fontWeight: FontWeight.bold)),
                  Expanded(child: Text(item['name'] ?? '')),
                  Text('\$${item['total_price']?.toStringAsFixed(2) ?? '0.00'}'),
                ],
              ),
            )),
            
            const Divider(height: 24),
            
            // Total
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('المجموع:', style: TextStyle(fontWeight: FontWeight.bold)),
                Text(
                  '\$${order['total_amount']?.toStringAsFixed(2) ?? '0.00'}',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Theme.of(context).colorScheme.primary,
                    fontSize: 18,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Actions
            if (status != 'delivered' && status != 'cancelled')
              Row(
                children: [
                  if (status == 'new')
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => _showCancelDialog(context, order['id']),
                        style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
                        child: const Text('رفض'),
                      ),
                    ),
                  if (status == 'new') const SizedBox(width: 16),
                  Expanded(
                    child: FilledButton(
                      onPressed: () => controller.updateOrderStatus(
                        order['id'],
                        controller.getNextStatus(status),
                      ),
                      child: Text(_getActionLabel(status)),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusChip(String status) {
    Color color;
    switch (status) {
      case 'new':
        color = Colors.blue;
        break;
      case 'accepted':
        color = Colors.orange;
        break;
      case 'preparing':
        color = Colors.purple;
        break;
      case 'ready':
        color = Colors.green;
        break;
      default:
        color = Colors.grey;
    }

    return Chip(
      label: Text(
        controller.getStatusLabel(status),
        style: const TextStyle(color: Colors.white, fontSize: 12),
      ),
      backgroundColor: color,
      padding: EdgeInsets.zero,
    );
  }

  String _getActionLabel(String status) {
    switch (status) {
      case 'new':
        return 'قبول';
      case 'accepted':
        return 'بدء التحضير';
      case 'preparing':
        return 'جاهز';
      case 'ready':
        return 'خرج للتوصيل';
      default:
        return 'التالي';
    }
  }

  void _showCancelDialog(BuildContext context, int orderId) {
    Get.dialog(
      AlertDialog(
        title: const Text('رفض الطلب'),
        content: const Text('هل أنت متأكد من رفض هذا الطلب؟'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Get.back();
              controller.updateOrderStatus(orderId, 'cancelled');
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('رفض'),
          ),
        ],
      ),
    );
  }
}
