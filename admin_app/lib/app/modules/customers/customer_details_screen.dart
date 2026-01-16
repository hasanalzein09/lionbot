import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';

class CustomerDetailsScreen extends StatefulWidget {
  final Map<String, dynamic> customer;

  const CustomerDetailsScreen({super.key, required this.customer});

  @override
  State<CustomerDetailsScreen> createState() => _CustomerDetailsScreenState();
}

class _CustomerDetailsScreenState extends State<CustomerDetailsScreen> {
  List<dynamic> _addresses = [];
  List<dynamic> _orders = [];
  bool _isLoadingAddresses = true;
  bool _isLoadingOrders = true;
  bool _hasChanges = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    await Future.wait([
      _loadAddresses(),
      _loadOrders(),
    ]);
  }

  Future<void> _loadAddresses() async {
    setState(() => _isLoadingAddresses = true);
    try {
      final addresses = await ApiService().getUserAddresses(widget.customer['id']);
      if (mounted) setState(() { _addresses = addresses; _isLoadingAddresses = false; });
    } catch (e) {
      if (mounted) setState(() => _isLoadingAddresses = false);
    }
  }

  Future<void> _loadOrders() async {
    setState(() => _isLoadingOrders = true);
    try {
      final orders = await ApiService().getUserOrders(widget.customer['id']);
      if (mounted) setState(() { _orders = orders; _isLoadingOrders = false; });
    } catch (e) {
      if (mounted) setState(() => _isLoadingOrders = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final customer = widget.customer;
    final name = customer['full_name'] ?? 'Unknown';
    final phone = customer['phone_number'] ?? '';
    final isActive = customer['is_active'] as bool? ?? true;

    return WillPopScope(
      onWillPop: () async {
        Navigator.pop(context, _hasChanges);
        return false;
      },
      child: Scaffold(
        appBar: AppBar(
          title: Text(name),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _loadData,
            ),
          ],
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Customer Info Card
              _buildInfoCard(name, phone, isActive),
              const SizedBox(height: 24),

              // Addresses Section
              _buildSectionHeader('Addresses', Icons.location_on, onAdd: _showAddAddressDialog),
              const SizedBox(height: 12),
              _buildAddressesSection(),
              const SizedBox(height: 24),

              // Orders Section
              _buildSectionHeader('Order History', Icons.receipt_long),
              const SizedBox(height: 12),
              _buildOrdersSection(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoCard(String name, String phone, bool isActive) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 36,
            backgroundColor: AppTheme.primaryColor.withAlpha(25),
            child: Text(
              name.isNotEmpty ? name[0].toUpperCase() : '?',
              style: const TextStyle(
                color: AppTheme.primaryColor,
                fontWeight: FontWeight.bold,
                fontSize: 28,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    const Icon(Icons.phone, size: 16, color: AppTheme.textMuted),
                    const SizedBox(width: 6),
                    Text(phone.isNotEmpty ? phone : 'No phone', style: const TextStyle(color: AppTheme.textMuted)),
                  ],
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: isActive ? AppTheme.accentColor.withAlpha(25) : AppTheme.errorColor.withAlpha(25),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    isActive ? 'Active' : 'Inactive',
                    style: TextStyle(
                      color: isActive ? AppTheme.accentColor : AppTheme.errorColor,
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon, {VoidCallback? onAdd}) {
    return Row(
      children: [
        Icon(icon, color: AppTheme.primaryColor, size: 22),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const Spacer(),
        if (onAdd != null)
          IconButton(
            icon: const Icon(Icons.add_circle, color: AppTheme.accentColor),
            onPressed: onAdd,
            tooltip: 'Add',
          ),
      ],
    );
  }

  Widget _buildAddressesSection() {
    if (_isLoadingAddresses) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: CircularProgressIndicator(color: AppTheme.primaryColor),
        ),
      );
    }

    if (_addresses.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: AppTheme.cardDark,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: Column(
            children: [
              Icon(Icons.location_off, size: 48, color: Colors.white.withAlpha(76)),
              const SizedBox(height: 12),
              Text(
                'No addresses saved',
                style: TextStyle(color: Colors.white.withAlpha(127)),
              ),
              const SizedBox(height: 12),
              TextButton.icon(
                icon: const Icon(Icons.add),
                label: const Text('Add Address'),
                onPressed: _showAddAddressDialog,
              ),
            ],
          ),
        ),
      );
    }

    return Column(
      children: _addresses.map((address) => _buildAddressCard(address)).toList(),
    );
  }

  Widget _buildAddressCard(Map<String, dynamic> address) {
    final label = address['label'] ?? 'Address';
    final addressText = address['address'] ?? '';
    final isDefault = address['is_default'] as bool? ?? false;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(12),
        border: isDefault ? Border.all(color: AppTheme.primaryColor, width: 1) : null,
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AppTheme.primaryColor.withAlpha(25),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(
              _getAddressIcon(label),
              color: AppTheme.primaryColor,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      label,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    if (isDefault) ...[
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppTheme.accentColor.withAlpha(25),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Text(
                          'Default',
                          style: TextStyle(color: AppTheme.accentColor, fontSize: 10),
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  addressText,
                  style: TextStyle(color: Colors.white.withAlpha(153), fontSize: 13),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert, color: AppTheme.textMuted),
            color: AppTheme.surfaceDark,
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'edit',
                child: Row(children: [
                  Icon(Icons.edit, size: 18, color: AppTheme.primaryColor),
                  SizedBox(width: 8),
                  Text('Edit'),
                ]),
              ),
              const PopupMenuItem(
                value: 'delete',
                child: Row(children: [
                  Icon(Icons.delete, size: 18, color: AppTheme.errorColor),
                  SizedBox(width: 8),
                  Text('Delete', style: TextStyle(color: AppTheme.errorColor)),
                ]),
              ),
            ],
            onSelected: (action) => _handleAddressAction(address, action),
          ),
        ],
      ),
    );
  }

  IconData _getAddressIcon(String label) {
    final lower = label.toLowerCase();
    if (lower.contains('home')) return Icons.home;
    if (lower.contains('work') || lower.contains('office')) return Icons.work;
    return Icons.location_on;
  }

  Widget _buildOrdersSection() {
    if (_isLoadingOrders) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: CircularProgressIndicator(color: AppTheme.primaryColor),
        ),
      );
    }

    if (_orders.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: AppTheme.cardDark,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: Column(
            children: [
              Icon(Icons.receipt_long, size: 48, color: Colors.white.withAlpha(76)),
              const SizedBox(height: 12),
              Text(
                'No orders yet',
                style: TextStyle(color: Colors.white.withAlpha(127)),
              ),
            ],
          ),
        ),
      );
    }

    return Column(
      children: _orders.take(10).map((order) => _buildOrderCard(order)).toList(),
    );
  }

  Widget _buildOrderCard(Map<String, dynamic> order) {
    final status = order['status'] as String? ?? 'unknown';
    final total = (order['total_amount'] ?? 0).toDouble();
    final createdAt = order['created_at'] as String?;

    Color statusColor;
    switch (status) {
      case 'delivered':
        statusColor = AppTheme.accentColor;
        break;
      case 'cancelled':
        statusColor = AppTheme.errorColor;
        break;
      case 'new':
      case 'preparing':
        statusColor = AppTheme.warningColor;
        break;
      default:
        statusColor = AppTheme.primaryColor;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: statusColor.withAlpha(25),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(Icons.receipt, color: statusColor, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Order #${order['id']}',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Text(
                  createdAt != null ? _formatDate(createdAt) : '',
                  style: TextStyle(color: Colors.white.withAlpha(127), fontSize: 12),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '\$${total.toStringAsFixed(2)}',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: statusColor.withAlpha(25),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  status.toUpperCase().replaceAll('_', ' '),
                  style: TextStyle(color: statusColor, fontSize: 10, fontWeight: FontWeight.w500),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _formatDate(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return dateStr;
    }
  }

  void _handleAddressAction(Map<String, dynamic> address, String action) {
    switch (action) {
      case 'edit':
        _showEditAddressDialog(address);
        break;
      case 'delete':
        _showDeleteAddressConfirmation(address);
        break;
    }
  }

  void _showAddAddressDialog() {
    final labelController = TextEditingController();
    final addressController = TextEditingController();
    bool isDefault = false;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          backgroundColor: AppTheme.cardDark,
          title: const Text('Add Address'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: labelController,
                  decoration: const InputDecoration(
                    labelText: 'Label (e.g., Home, Work)',
                    prefixIcon: Icon(Icons.label),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: addressController,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    labelText: 'Address',
                    prefixIcon: Icon(Icons.location_on),
                    alignLabelWithHint: true,
                  ),
                ),
                const SizedBox(height: 16),
                SwitchListTile(
                  title: const Text('Set as default'),
                  value: isDefault,
                  onChanged: (v) => setDialogState(() => isDefault = v),
                  activeColor: AppTheme.primaryColor,
                  contentPadding: EdgeInsets.zero,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (labelController.text.isEmpty || addressController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Please fill all fields')),
                  );
                  return;
                }
                Navigator.pop(context);
                await _createAddress(labelController.text, addressController.text, isDefault);
              },
              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryColor),
              child: const Text('Add', style: TextStyle(color: Colors.black)),
            ),
          ],
        ),
      ),
    );
  }

  void _showEditAddressDialog(Map<String, dynamic> address) {
    final labelController = TextEditingController(text: address['label'] ?? '');
    final addressController = TextEditingController(text: address['address'] ?? '');
    bool isDefault = address['is_default'] as bool? ?? false;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          backgroundColor: AppTheme.cardDark,
          title: const Text('Edit Address'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: labelController,
                  decoration: const InputDecoration(
                    labelText: 'Label',
                    prefixIcon: Icon(Icons.label),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: addressController,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    labelText: 'Address',
                    prefixIcon: Icon(Icons.location_on),
                    alignLabelWithHint: true,
                  ),
                ),
                const SizedBox(height: 16),
                SwitchListTile(
                  title: const Text('Set as default'),
                  value: isDefault,
                  onChanged: (v) => setDialogState(() => isDefault = v),
                  activeColor: AppTheme.primaryColor,
                  contentPadding: EdgeInsets.zero,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(context);
                await _updateAddress(address['id'], labelController.text, addressController.text, isDefault);
              },
              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryColor),
              child: const Text('Save', style: TextStyle(color: Colors.black)),
            ),
          ],
        ),
      ),
    );
  }

  void _showDeleteAddressConfirmation(Map<String, dynamic> address) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.cardDark,
        title: const Text('Delete Address'),
        content: Text('Are you sure you want to delete "${address['label']}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              await _deleteAddress(address['id']);
            },
            child: const Text('Delete', style: TextStyle(color: AppTheme.errorColor)),
          ),
        ],
      ),
    );
  }

  Future<void> _createAddress(String label, String address, bool isDefault) async {
    try {
      await ApiService().createUserAddress(widget.customer['id'], {
        'label': label,
        'address': address,
        'is_default': isDefault,
      });
      _hasChanges = true;
      _loadAddresses();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Address added'), backgroundColor: AppTheme.accentColor),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to add address: $e'), backgroundColor: AppTheme.errorColor),
        );
      }
    }
  }

  Future<void> _updateAddress(int addressId, String label, String address, bool isDefault) async {
    try {
      await ApiService().updateAddress(addressId, {
        'label': label,
        'address': address,
        'is_default': isDefault,
      });
      _hasChanges = true;
      _loadAddresses();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Address updated'), backgroundColor: AppTheme.accentColor),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to update address: $e'), backgroundColor: AppTheme.errorColor),
        );
      }
    }
  }

  Future<void> _deleteAddress(int addressId) async {
    try {
      await ApiService().deleteAddress(addressId);
      _hasChanges = true;
      _loadAddresses();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Address deleted'), backgroundColor: AppTheme.accentColor),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to delete address: $e'), backgroundColor: AppTheme.errorColor),
        );
      }
    }
  }
}
