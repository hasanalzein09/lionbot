import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';

class InventoryScreen extends StatefulWidget {
  const InventoryScreen({super.key});

  @override
  State<InventoryScreen> createState() => _InventoryScreenState();
}

class _InventoryScreenState extends State<InventoryScreen> {
  List<dynamic> _restaurants = [];
  int? _selectedRestaurant;
  List<dynamic> _items = [];
  Map<String, dynamic>? _value;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadRestaurants();
  }

  Future<void> _loadRestaurants() async {
    final restaurants = await ApiService().getRestaurants();
    if (mounted) {
      setState(() {
        _restaurants = restaurants;
        if (restaurants.isNotEmpty) {
          _selectedRestaurant = restaurants[0]['id'];
          _loadInventory();
        } else {
          _isLoading = false;
        }
      });
    }
  }

  Future<void> _loadInventory() async {
    if (_selectedRestaurant == null) return;
    setState(() => _isLoading = true);
    try {
      final items = await ApiService().getInventory(_selectedRestaurant!);
      final value = await ApiService().getInventoryValue(_selectedRestaurant!);
      if (mounted) setState(() { _items = items; _value = value; _isLoading = false; });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Inventory'),
        actions: [
          IconButton(icon: const Icon(Icons.warning_amber), onPressed: () => _showLowStock()),
        ],
      ),
      body: Column(
        children: [
          // Restaurant Selector
          Container(
            padding: const EdgeInsets.all(16),
            child: DropdownButtonFormField<int>(
              value: _selectedRestaurant,
              decoration: const InputDecoration(labelText: 'Select Restaurant'),
              items: _restaurants.map<DropdownMenuItem<int>>((r) {
                return DropdownMenuItem<int>(value: r['id'], child: Text(r['name'] ?? ''));
              }).toList(),
              onChanged: (v) {
                setState(() { _selectedRestaurant = v; });
                _loadInventory();
              },
            ),
          ),
          
          // Value Summary
          if (_value != null)
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: [AppTheme.primaryColor.withOpacity(0.2), AppTheme.accentColor.withOpacity(0.1)]),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildValueItem('Total Value', '\$${(_value!['total_value'] ?? 0).toStringAsFixed(2)}'),
                  _buildValueItem('Items', '${_value!['total_items'] ?? 0}'),
                  _buildValueItem('Low Stock', '${_value!['low_stock_count'] ?? 0}', color: AppTheme.warningColor),
                ],
              ),
            ),
          
          const SizedBox(height: 16),
          
          // Items List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryColor))
                : ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: _items.length,
                    itemBuilder: (context, index) => _buildItemCard(_items[index]),
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppTheme.primaryColor,
        child: const Icon(Icons.add, color: Colors.black),
        onPressed: () {},
      ),
    );
  }

  Widget _buildValueItem(String label, String value, {Color? color}) {
    return Column(
      children: [
        Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.white.withOpacity(0.6))),
      ],
    );
  }

  Widget _buildItemCard(Map<String, dynamic> item) {
    final isLow = item['is_low_stock'] as bool? ?? false;
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(12),
        border: isLow ? Border.all(color: AppTheme.warningColor.withOpacity(0.5)) : null,
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: (isLow ? AppTheme.warningColor : AppTheme.primaryColor).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(Icons.inventory_2, color: isLow ? AppTheme.warningColor : AppTheme.primaryColor),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item['name'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
                Text('${item['current_quantity']} ${item['unit']}', style: TextStyle(color: Colors.white.withOpacity(0.6))),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text('\$${(item['average_cost'] ?? 0).toStringAsFixed(2)}', style: const TextStyle(fontWeight: FontWeight.bold)),
              if (isLow) const Text('LOW', style: TextStyle(color: AppTheme.warningColor, fontSize: 10, fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      ),
    );
  }

  void _showLowStock() async {
    if (_selectedRestaurant == null) return;
    final lowStock = await ApiService().getLowStockItems(_selectedRestaurant!);
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.cardDark,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Low Stock Alerts', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            ...lowStock.map((item) => ListTile(
              leading: const Icon(Icons.warning, color: AppTheme.warningColor),
              title: Text(item['name'] ?? ''),
              subtitle: Text('${item['current_quantity']} / ${item['min_quantity']} ${item['unit']}'),
            )),
          ],
        ),
      ),
    );
  }
}
