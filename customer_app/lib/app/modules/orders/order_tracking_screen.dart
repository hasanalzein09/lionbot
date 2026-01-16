import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/theme/app_theme.dart';

class OrderTrackingScreen extends StatelessWidget {
  const OrderTrackingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final order = Get.arguments as Map<String, dynamic>? ?? {};
    return Scaffold(
      appBar: AppBar(title: Text('track_order'.tr)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildTimeline(order['status'] ?? 'pending'),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Order Details', style: TextStyle(fontWeight: FontWeight.bold)),
                  const Divider(),
                  Text('Order #${order['id']}'),
                  Text('Total: \$${order['total_amount'] ?? 0}'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeline(String current) {
    final statuses = ['order_placed', 'preparing', 'on_the_way', 'delivered'];
    final idx = statuses.indexOf(current.contains('delivery') ? 'on_the_way' : current);
    return Column(
      children: List.generate(statuses.length, (i) => Row(
        children: [
          Column(children: [
            CircleAvatar(radius: 12, backgroundColor: i <= idx ? AppTheme.primaryColor : Colors.grey[300],
              child: i <= idx ? const Icon(Icons.check, size: 16, color: Colors.white) : null),
            if (i < 3) Container(width: 2, height: 40, color: i < idx ? AppTheme.primaryColor : Colors.grey[300]),
          ]),
          const SizedBox(width: 16),
          Text(statuses[i].tr, style: TextStyle(fontWeight: i == idx ? FontWeight.bold : FontWeight.normal)),
        ],
      )),
    );
  }
}
