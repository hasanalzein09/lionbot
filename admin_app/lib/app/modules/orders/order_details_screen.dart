import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';

class OrderDetailsScreen extends StatefulWidget {
  final int? orderId;
  const OrderDetailsScreen({super.key, this.orderId});

  @override
  State<OrderDetailsScreen> createState() => _OrderDetailsScreenState();
}

class _OrderDetailsScreenState extends State<OrderDetailsScreen> {
  Map<String, dynamic>? _order;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadOrder();
  }

  Future<void> _loadOrder() async {
    if (widget.orderId == null) return;
    try {
      final order = await ApiService().getOrder(widget.orderId!);
      if (mounted) setState(() { _order = order; _isLoading = false; });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _updateStatus(String status) async {
    try {
      await ApiService().updateOrderStatus(widget.orderId!, status);
      _loadOrder();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Status updated to $status')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to update status')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Order #${widget.orderId}')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryColor))
          : _order == null
              ? const Center(child: Text('Order not found'))
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildStatusCard(),
                      const SizedBox(height: 16),
                      _buildInfoCard(),
                      const SizedBox(height: 16),
                      _buildItemsCard(),
                      const SizedBox(height: 16),
                      _buildDriverCard(),
                      const SizedBox(height: 16),
                      _buildActionsCard(),
                    ],
                  ),
                ),
    );
  }

  Widget _buildStatusCard() {
    final status = _order!['status'] as String;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.primaryColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.receipt_long, color: AppTheme.primaryColor, size: 32),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(status.toUpperCase().replaceAll('_', ' '),
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text('\$${(_order!['total_amount'] ?? 0).toStringAsFixed(2)}',
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.primaryColor)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: AppTheme.cardDark, borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          _buildInfoRow(Icons.restaurant, 'Restaurant', _order!['restaurant_name'] ?? _order!['restaurant_name_ar'] ?? 'N/A'),
          const Divider(height: 24),
          _buildInfoRow(Icons.person, 'Customer', _order!['customer_name'] ?? 'N/A'),
          const Divider(height: 24),
          _buildInfoRow(Icons.phone, 'Phone', _order!['customer_phone'] ?? 'N/A'),
          const Divider(height: 24),
          _buildInfoRow(Icons.location_on, 'Address', _order!['address'] ?? 'N/A'),
        ],
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 20, color: AppTheme.textMuted),
        const SizedBox(width: 12),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(fontSize: 12, color: AppTheme.textMuted)),
            Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
          ],
        ),
      ],
    );
  }

  Widget _buildItemsCard() {
    final items = _order!['items'] as List<dynamic>? ?? [];
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: AppTheme.cardDark, borderRadius: BorderRadius.circular(16)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Order Items', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 12),
          if (items.isEmpty)
            const Text('No items', style: TextStyle(color: AppTheme.textMuted))
          else
            ...items.map((item) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(child: Text('${item['quantity']}x ${item['name'] ?? item['name_ar'] ?? 'Item'}')),
                  Text('\$${(item['total_price'] ?? item['unit_price'] ?? 0).toStringAsFixed(2)}'),
                ],
              ),
            )),
        ],
      ),
    );
  }

  Widget _buildDriverCard() {
    final driverName = _order!['driver_name'] as String?;
    final driverId = _order!['driver_id'] as int?;
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: AppTheme.cardDark, borderRadius: BorderRadius.circular(16)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Driver Assignment', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              if (driverId == null)
                TextButton.icon(
                  icon: const Icon(Icons.auto_fix_high, size: 18),
                  label: const Text('Auto-Assign'),
                  style: TextButton.styleFrom(foregroundColor: AppTheme.primaryColor),
                  onPressed: _autoAssignDriver,
                ),
            ],
          ),
          const SizedBox(height: 12),
          if (driverId != null)
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: AppTheme.accentColor.withOpacity(0.1),
                  child: const Icon(Icons.delivery_dining, color: AppTheme.accentColor),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(driverName ?? 'Driver #$driverId', style: const TextStyle(fontWeight: FontWeight.bold)),
                      const Text('Assigned', style: TextStyle(color: AppTheme.accentColor, fontSize: 12)),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.swap_horiz, color: AppTheme.textMuted),
                  onPressed: _showDriverPicker,
                  tooltip: 'Change Driver',
                ),
              ],
            )
          else
            InkWell(
              onTap: _showDriverPicker,
              borderRadius: BorderRadius.circular(12),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  border: Border.all(color: AppTheme.textMuted.withOpacity(0.3), style: BorderStyle.solid),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.person_add, color: AppTheme.textMuted),
                    SizedBox(width: 8),
                    Text('Select Driver', style: TextStyle(color: AppTheme.textMuted)),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Future<void> _autoAssignDriver() async {
    try {
      await ApiService().autoAssignDriver(widget.orderId!);
      _loadOrder();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Driver auto-assigned!'), backgroundColor: AppTheme.accentColor),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Auto-assign failed: $e'), backgroundColor: AppTheme.errorColor),
        );
      }
    }
  }

  void _showDriverPicker() async {
    try {
      final drivers = await ApiService().getDrivers();
      if (!mounted) return;
      
      showModalBottomSheet(
        context: context,
        backgroundColor: AppTheme.cardDark,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        builder: (context) => Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Select Driver', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
              const SizedBox(height: 16),
              if (drivers.isEmpty)
                const Center(child: Text('No drivers available'))
              else
                ...drivers.take(5).map((d) => ListTile(
                  leading: CircleAvatar(
                    backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
                    child: Text(d['full_name']?[0] ?? 'D', style: const TextStyle(color: AppTheme.primaryColor)),
                  ),
                  title: Text(d['full_name'] ?? 'Driver'),
                  subtitle: Text(d['phone_number'] ?? ''),
                  trailing: (d['is_active'] ?? false)
                      ? Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppTheme.accentColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Text('Online', style: TextStyle(color: AppTheme.accentColor, fontSize: 11)),
                        )
                      : null,
                  onTap: () async {
                    Navigator.pop(context);
                    await _assignDriver(d['id']);
                  },
                )),
            ],
          ),
        ),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load drivers: $e'), backgroundColor: AppTheme.errorColor),
        );
      }
    }
  }

  Future<void> _assignDriver(int driverId) async {
    try {
      await ApiService().assignDriverToOrder(widget.orderId!, driverId);
      _loadOrder();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Driver assigned!'), backgroundColor: AppTheme.accentColor),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Assignment failed: $e'), backgroundColor: AppTheme.errorColor),
        );
      }
    }
  }

  Widget _buildActionsCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: AppTheme.cardDark, borderRadius: BorderRadius.circular(16)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text('Update Status', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildStatusButton('preparing', 'Preparing', Colors.blueAccent),
              _buildStatusButton('ready', 'Ready', Colors.purpleAccent),
              _buildStatusButton('out_for_delivery', 'Out for Delivery', AppTheme.primaryColor),
              _buildStatusButton('delivered', 'Delivered', AppTheme.accentColor),
              _buildStatusButton('cancelled', 'Cancel', AppTheme.errorColor),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatusButton(String status, String label, Color color) {
    return ElevatedButton(
      onPressed: () => _updateStatus(status),
      style: ElevatedButton.styleFrom(
        backgroundColor: color.withOpacity(0.2),
        foregroundColor: color,
      ),
      child: Text(label),
    );
  }
}
