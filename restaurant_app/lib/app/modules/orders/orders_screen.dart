import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:timeago/timeago.dart' as timeago;

import '../../core/theme/app_theme.dart';

class OrdersScreen extends StatefulWidget {
  const OrdersScreen({super.key});

  @override
  State<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends State<OrdersScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<dynamic> _orders = [];
  bool _isLoading = true;
  String _filter = 'all';

  final _tabs = [
    {'label': 'All', 'value': 'all'},
    {'label': 'New', 'value': 'pending'},
    {'label': 'Preparing', 'value': 'preparing'},
    {'label': 'Ready', 'value': 'ready'},
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _tabs.length, vsync: this);
    _tabController.addListener(() {
      if (!_tabController.indexIsChanging) {
        setState(() => _filter = _tabs[_tabController.index]['value']!);
        _loadOrders();
      }
    });
    _loadOrders();
  }

  Future<void> _loadOrders() async {
    final token = await const FlutterSecureStorage().read(key: 'token');
    final restaurantId = await const FlutterSecureStorage().read(key: 'restaurant_id');
    
    try {
      final dio = Dio(BaseOptions(
        baseUrl: 'https://lionbot-backend-426202982674.me-west1.run.app/api/v1',
        headers: {'Authorization': 'Bearer $token'},
      ));
      
      final params = {'restaurant_id': restaurantId};
      if (_filter != 'all') params['status'] = _filter;
      
      final response = await dio.get('/orders/', queryParameters: params);
      if (mounted) setState(() { _orders = response.data; _isLoading = false; });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _updateStatus(int orderId, String status) async {
    final token = await const FlutterSecureStorage().read(key: 'token');
    try {
      final dio = Dio(BaseOptions(
        baseUrl: 'https://lionbot-backend-426202982674.me-west1.run.app/api/v1',
        headers: {'Authorization': 'Bearer $token'},
      ));
      await dio.patch('/orders/$orderId/', data: {'status': status});
      _loadOrders();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Order #$orderId updated to $status')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to update order')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Orders'),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _loadOrders)],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppTheme.primaryColor,
          labelColor: AppTheme.primaryColor,
          unselectedLabelColor: AppTheme.textMuted,
          tabs: _tabs.map((t) => Tab(text: t['label'])).toList(),
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryColor))
          : RefreshIndicator(
              onRefresh: _loadOrders,
              child: _orders.isEmpty
                  ? Center(child: Text('No orders', style: TextStyle(color: Colors.white.withOpacity(0.5))))
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _orders.length,
                      itemBuilder: (context, index) => _buildOrderCard(_orders[index]),
                    ),
            ),
    );
  }

  Widget _buildOrderCard(Map<String, dynamic> order) {
    final status = order['status'] as String;
    final statusColor = _getStatusColor(status);
    final createdAt = DateTime.parse(order['created_at']);
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: statusColor.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Order #${order['id']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(color: statusColor.withOpacity(0.1), borderRadius: BorderRadius.circular(20)),
                child: Text(status.toUpperCase(), style: TextStyle(color: statusColor, fontSize: 11, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          const SizedBox(height: 12),
          
          // Items
          ...((order['items'] as List?) ?? []).take(3).map((item) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Text('${item['quantity']}x ${item['name']}', style: TextStyle(color: Colors.white.withOpacity(0.7))),
          )),
          
          const Divider(height: 24),
          
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(timeago.format(createdAt), style: TextStyle(fontSize: 12, color: Colors.white.withOpacity(0.5))),
              Text('\$${(order['total_amount'] ?? 0).toStringAsFixed(2)}',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.primaryColor)),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Action Buttons
          Row(
            children: [
              if (status == 'pending')
                Expanded(child: _buildActionBtn('Accept', AppTheme.accentColor, () => _updateStatus(order['id'], 'preparing'))),
              if (status == 'preparing')
                Expanded(child: _buildActionBtn('Mark Ready', AppTheme.statusReady, () => _updateStatus(order['id'], 'ready'))),
              if (status == 'ready')
                Expanded(child: _buildActionBtn('Picked Up', AppTheme.statusDelivered, () => _updateStatus(order['id'], 'out_for_delivery'))),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActionBtn(String label, Color color, VoidCallback onTap) {
    return ElevatedButton(
      onPressed: onTap,
      style: ElevatedButton.styleFrom(backgroundColor: color),
      child: Text(label),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'pending': return AppTheme.statusPending;
      case 'preparing': return AppTheme.statusPreparing;
      case 'ready': return AppTheme.statusReady;
      case 'out_for_delivery': return AppTheme.statusDelivery;
      case 'delivered': return AppTheme.statusDelivered;
      case 'cancelled': return AppTheme.statusCancelled;
      default: return AppTheme.textMuted;
    }
  }
}

class OrderDetailsScreen extends StatelessWidget {
  final int? orderId;
  const OrderDetailsScreen({super.key, this.orderId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Order #$orderId')),
      body: const Center(child: Text('Order Details')),
    );
  }
}
