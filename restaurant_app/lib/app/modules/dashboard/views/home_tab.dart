import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../controllers/dashboard_controller.dart';

class HomeTab extends GetView<DashboardController> {
  const HomeTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Obx(() => Text(controller.restaurantName.value.isEmpty 
            ? 'مطعمي' 
            : controller.restaurantName.value)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: controller.loadData,
          ),
        ],
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }
        
        return RefreshIndicator(
          onRefresh: controller.loadData,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Welcome
                Text(
                  'مرحباً ${controller.userName.value}',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 8),
                Text(
                  'إليك ملخص اليوم',
                  style: TextStyle(color: Colors.grey[600]),
                ),
                
                const SizedBox(height: 24),
                
                // Stats Grid
                GridView.count(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  crossAxisCount: 2,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  childAspectRatio: 1.3,
                  children: [
                    _buildStatCard(
                      context,
                      'طلبات اليوم',
                      controller.todayOrders.value.toString(),
                      Icons.receipt_long,
                      Colors.blue,
                    ),
                    _buildStatCard(
                      context,
                      'طلبات معلقة',
                      controller.pendingOrders.value.toString(),
                      Icons.pending_actions,
                      Colors.orange,
                    ),
                    _buildStatCard(
                      context,
                      'الإيرادات',
                      '\$${controller.totalRevenue.value.toStringAsFixed(2)}',
                      Icons.attach_money,
                      Colors.green,
                    ),
                    _buildStatCard(
                      context,
                      'أصناف القائمة',
                      controller.menuItemsCount.value.toString(),
                      Icons.restaurant_menu,
                      Colors.purple,
                    ),
                  ],
                ),
                
                const SizedBox(height: 32),
                
                // Quick Actions
                Text(
                  'إجراءات سريعة',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 16),
                
                _buildActionButton(
                  context,
                  'عرض الطلبات',
                  Icons.list_alt,
                  () => controller.changeTab(1),
                ),
                const SizedBox(height: 12),
                _buildActionButton(
                  context,
                  'إدارة القائمة',
                  Icons.menu_book,
                  () => controller.changeTab(2),
                ),
              ],
            ),
          ),
        );
      }),
    );
  }

  Widget _buildStatCard(
    BuildContext context,
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              title,
              style: TextStyle(color: Colors.grey[600], fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton(
    BuildContext context,
    String title,
    IconData icon,
    VoidCallback onPressed,
  ) {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon),
        label: Text(title),
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(vertical: 16),
        ),
      ),
    );
  }
}
