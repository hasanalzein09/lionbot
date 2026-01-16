import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/theme/app_theme.dart';
import '../../routes/app_routes.dart';

class CheckoutScreen extends StatelessWidget {
  const CheckoutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('checkout'.tr)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Delivery Address
            Text('delivery_address'.tr, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.primaryColor),
              ),
              child: Row(
                children: [
                  const Icon(Icons.location_on, color: AppTheme.primaryColor),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Home', style: TextStyle(fontWeight: FontWeight.bold)),
                        Text('123 Main Street, Downtown', style: TextStyle(color: Colors.grey[600])),
                      ],
                    ),
                  ),
                  TextButton(onPressed: () {}, child: const Text('Change')),
                ],
              ),
            ),
            const SizedBox(height: 24),
            
            // Payment Method
            Text('payment_method'.tr, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.primaryColor),
              ),
              child: Row(
                children: [
                  const Icon(Icons.money, color: AppTheme.accentColor),
                  const SizedBox(width: 12),
                  Expanded(child: Text('cash_on_delivery'.tr, style: const TextStyle(fontWeight: FontWeight.bold))),
                  const Icon(Icons.check_circle, color: AppTheme.primaryColor),
                ],
              ),
            ),
            const SizedBox(height: 24),
            
            // Order Notes
            Text('order_notes'.tr, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            TextField(
              maxLines: 3,
              decoration: InputDecoration(
                hintText: 'Add notes for your order...',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 24),
            
            // Summary
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(color: Colors.grey.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
              child: Column(
                children: [
                  _buildRow('subtotal'.tr, '\$23.96'),
                  _buildRow('delivery_fee'.tr, '\$2.00'),
                  const Divider(),
                  _buildRow('total'.tr, '\$25.96', isBold: true),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(16),
        child: SizedBox(
          height: 56,
          child: ElevatedButton(
            onPressed: () {
              Get.snackbar('success'.tr, 'Order placed successfully!');
              Get.offAllNamed(AppRoutes.home);
            },
            child: Text('place_order'.tr),
          ),
        ),
      ),
    );
  }

  Widget _buildRow(String label, String value, {bool isBold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontWeight: isBold ? FontWeight.bold : FontWeight.normal)),
          Text(value, style: TextStyle(fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
            color: isBold ? AppTheme.primaryColor : null)),
        ],
      ),
    );
  }
}
