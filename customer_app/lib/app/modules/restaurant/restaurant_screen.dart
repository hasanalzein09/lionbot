import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';

class RestaurantScreen extends StatefulWidget {
  const RestaurantScreen({super.key});
  @override
  State<RestaurantScreen> createState() => _RestaurantScreenState();
}

class _RestaurantScreenState extends State<RestaurantScreen> {
  List<dynamic> _menuItems = [];
  bool _isLoading = true;
  late Map<String, dynamic> _restaurant;

  @override
  void initState() {
    super.initState();
    _restaurant = Get.arguments as Map<String, dynamic>;
    _loadMenu();
  }

  Future<void> _loadMenu() async {
    try {
      final menu = await ApiService().getRestaurantMenu(_restaurant['id']);
      if (mounted) setState(() { _menuItems = menu; _isLoading = false; });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App Bar with Image
          SliverAppBar(
            expandedHeight: 200,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              title: Text(_restaurant['name'] ?? ''),
              background: Container(
                color: AppTheme.primaryColor.withOpacity(0.2),
                child: Center(child: Icon(Icons.restaurant, size: 80, color: AppTheme.primaryColor)),
              ),
            ),
          ),
          
          // Restaurant Info
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  _buildInfoChip(Icons.star, '4.5'),
                  const SizedBox(width: 12),
                  _buildInfoChip(Icons.access_time, '30-40 ${'minutes'.tr}'),
                  const SizedBox(width: 12),
                  _buildInfoChip(Icons.delivery_dining, '\$2.00'),
                ],
              ),
            ),
          ),
          
          // Menu Header
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text('menu'.tr, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            ),
          ),
          
          // Menu Items
          _isLoading
              ? const SliverFillRemaining(child: Center(child: CircularProgressIndicator()))
              : SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) => _buildMenuItem(_menuItems[index]),
                    childCount: _menuItems.length,
                  ),
                ),
        ],
      ),
    );
  }

  Widget _buildInfoChip(IconData icon, String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.grey.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: AppTheme.primaryColor),
          const SizedBox(width: 4),
          Text(text, style: const TextStyle(fontSize: 12)),
        ],
      ),
    );
  }

  Widget _buildMenuItem(Map<String, dynamic> item) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8)],
      ),
      child: Row(
        children: [
          Container(
            width: 70, height: 70,
            decoration: BoxDecoration(
              color: AppTheme.lightSurface,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.fastfood, color: AppTheme.primaryColor),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item['name'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(item['description'] ?? '', maxLines: 2, overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                const SizedBox(height: 4),
                Text('\$${item['price'] ?? 0}', style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.add_circle, color: AppTheme.primaryColor, size: 32),
            onPressed: () => Get.snackbar('success'.tr, 'Added to cart'),
          ),
        ],
      ),
    );
  }
}
