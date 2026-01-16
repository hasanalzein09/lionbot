import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';
import '../../routes/app_routes.dart';

class OrdersScreen extends StatefulWidget {
  const OrdersScreen({super.key});
  @override
  State<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends State<OrdersScreen> {
  List<dynamic> _orders = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadOrders();
  }

  Future<void> _loadOrders() async {
    try {
      final orders = await ApiService().getMyOrders();
      if (mounted) setState(() { _orders = orders; _isLoading = false; });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('my_orders'.tr)),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _orders.isEmpty
              ? Center(child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.receipt_long, size: 80, color: Colors.grey[300]),
                    const SizedBox(height: 16),
                    Text('no_orders'.tr, style: TextStyle(color: Colors.grey[600])),
                  ],
                ))
              : RefreshIndicator(
                  onRefresh: _loadOrders,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _orders.length,
                    itemBuilder: (context, index) => _buildOrderCard(_orders[index]),
                  ),
                ),
    );
  }

  Widget _buildOrderCard(Map<String, dynamic> order) {
    final status = order['status'] as String? ?? 'pending';
    return GestureDetector(
      onTap: () => Get.toNamed(AppRoutes.orderTracking, arguments: order),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Order #${order['id']}', style: const TextStyle(fontWeight: FontWeight.bold)),
                _buildStatusBadge(status),
              ],
            ),
            const Divider(height: 16),
            Text(order['restaurant_name'] ?? 'Restaurant', style: TextStyle(color: Colors.grey[600])),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('\$${order['total_amount'] ?? 0}', style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primaryColor)),
                Text('track_order'.tr, style: const TextStyle(color: AppTheme.primaryColor)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(String status) {
    final colors = {
      'pending': Colors.orange,
      'preparing': Colors.blue,
      'out_for_delivery': AppTheme.primaryColor,
      'delivered': Colors.green,
      'cancelled': Colors.red,
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: (colors[status] ?? Colors.grey).withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(status.tr, style: TextStyle(color: colors[status], fontSize: 12, fontWeight: FontWeight.bold)),
    );
  }
}

class OrderTrackingScreen extends StatelessWidget {
  const OrderTrackingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final order = Get.arguments as Map<String, dynamic>? ?? {};
    return Scaffold(
      appBar: AppBar(title: Text('Order #${order['id']}')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Status Timeline
            _buildTimeline(order['status'] ?? 'pending'),
            const SizedBox(height: 24),
            
            // Order Summary
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Order Summary', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const Divider(),
                  Text('Restaurant: ${order['restaurant_name'] ?? 'N/A'}'),
                  Text('Total: \$${order['total_amount'] ?? 0}'),
                  Text('Payment: ${'cash_on_delivery'.tr}'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeline(String currentStatus) {
    final statuses = ['pending', 'preparing', 'out_for_delivery', 'delivered'];
    final currentIndex = statuses.indexOf(currentStatus);
    
    return Column(
      children: List.generate(statuses.length, (index) {
        final isActive = index <= currentIndex;
        final isCurrent = index == currentIndex;
        return Row(
          children: [
            Column(
              children: [
                Container(
                  width: 24, height: 24,
                  decoration: BoxDecoration(
                    color: isActive ? AppTheme.primaryColor : Colors.grey[300],
                    shape: BoxShape.circle,
                  ),
                  child: isActive ? const Icon(Icons.check, size: 16, color: Colors.white) : null,
                ),
                if (index < statuses.length - 1)
                  Container(width: 2, height: 40, color: isActive ? AppTheme.primaryColor : Colors.grey[300]),
              ],
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Text(statuses[index].tr,
                style: TextStyle(fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                  color: isActive ? Colors.black : Colors.grey)),
            ),
          ],
        );
      }),
    );
  }
}
