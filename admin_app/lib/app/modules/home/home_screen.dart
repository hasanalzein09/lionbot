import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:badges/badges.dart' as badges;

import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';
import '../../core/services/notification_service.dart';
import '../../routes/app_routes.dart';
import '../orders/orders_screen.dart';
import '../restaurants/restaurants_screen.dart';
import '../drivers/drivers_screen.dart';
import '../settings/settings_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _currentIndex = 0;
  int _notificationCount = 0;
  Map<String, dynamic>? _stats;
  bool _isLoading = true;

  // Store subscription for proper cleanup to prevent memory leaks
  StreamSubscription? _notificationSubscription;

  final List<Widget> _screens = [
    const DashboardTab(),
    const OrdersScreen(),
    const RestaurantsScreen(),
    const DriversScreen(),
    const SettingsScreen(),
  ];

  @override
  void initState() {
    super.initState();
    _loadStats();
    _listenToNotifications();
  }

  @override
  void dispose() {
    // Cancel subscription to prevent memory leaks
    _notificationSubscription?.cancel();
    super.dispose();
  }

  Future<void> _loadStats() async {
    try {
      final stats = await ApiService().getDashboardStats();
      if (mounted) {
        setState(() {
          _stats = stats;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _listenToNotifications() {
    final notifications = ref.read(notificationServiceProvider).onNewOrder;
    // Store subscription reference for cleanup
    _notificationSubscription = notifications.listen((order) {
      if (mounted) {
        setState(() {
          _notificationCount++;
        });
      }
    });
  }

  /// Safely get pending order count from stats with null safety
  int _getPendingOrderCount() {
    if (_stats == null) return 0;
    final orders = _stats!['orders'];
    if (orders == null) return 0;
    final pending = orders['pending'];
    if (pending == null) return 0;
    if (pending is int) return pending;
    if (pending is num) return pending.toInt();
    return int.tryParse(pending.toString()) ?? 0;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: AppTheme.cardDark,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.3),
              blurRadius: 10,
              offset: const Offset(0, -2),
            ),
          ],
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildNavItem(0, Icons.dashboard_rounded, 'Dashboard'),
                _buildNavItem(1, Icons.receipt_long_rounded, 'Orders', badge: _getPendingOrderCount()),
                _buildNavItem(2, Icons.restaurant_rounded, 'Restaurants'),
                _buildNavItem(3, Icons.delivery_dining_rounded, 'Drivers'),
                _buildNavItem(4, Icons.settings_rounded, 'Settings'),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(int index, IconData icon, String label, {int badge = 0}) {
    final isSelected = _currentIndex == index;
    
    return GestureDetector(
      onTap: () => setState(() => _currentIndex = index),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? AppTheme.primaryColor.withOpacity(0.1) : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            badge > 0
                ? badges.Badge(
                    badgeContent: Text(
                      badge > 99 ? '99+' : badge.toString(),
                      style: const TextStyle(color: Colors.white, fontSize: 10),
                    ),
                    badgeStyle: const badges.BadgeStyle(
                      badgeColor: AppTheme.errorColor,
                    ),
                    child: Icon(
                      icon,
                      color: isSelected ? AppTheme.primaryColor : AppTheme.textMuted,
                      size: 24,
                    ),
                  )
                : Icon(
                    icon,
                    color: isSelected ? AppTheme.primaryColor : AppTheme.textMuted,
                    size: 24,
                  ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                color: isSelected ? AppTheme.primaryColor : AppTheme.textMuted,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ==================== Dashboard Tab ====================

class DashboardTab extends StatefulWidget {
  const DashboardTab({super.key});

  @override
  State<DashboardTab> createState() => _DashboardTabState();
}

class _DashboardTabState extends State<DashboardTab> {
  Map<String, dynamic>? _stats;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final stats = await ApiService().getDashboardStats();
      if (mounted) {
        setState(() {
          _stats = stats;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() => _isLoading = true);
              _loadData();
            },
          ),
          IconButton(
            icon: const Icon(Icons.bar_chart_rounded),
            onPressed: () => Navigator.pushNamed(context, AppRoutes.stats),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        color: AppTheme.primaryColor,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryColor))
            : SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Stats Cards
                    _buildStatsGrid(),
                    const SizedBox(height: 24),
                    
                    // Quick Actions
                    const Text(
                      'Quick Actions',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 12),
                    _buildQuickActions(),
                    const SizedBox(height: 24),
                    
                    // Recent Activity
                    const Text(
                      'Recent Activity',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 12),
                    _buildRecentActivity(),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _buildStatsGrid() {
    // Extract nested values from API response
    final revenue = _stats?['revenue'] as Map<String, dynamic>?;
    final orders = _stats?['orders'] as Map<String, dynamic>?;
    final drivers = _stats?['drivers'] as Map<String, dynamic>?;

    final todayRevenue = (revenue?['today'] ?? 0).toDouble();
    final pendingOrders = orders?['pending'] ?? 0;
    final activeDrivers = drivers?['active'] ?? 0;
    final totalOrders = orders?['total'] ?? 0;

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.4,
      children: [
        _buildStatCard(
          'Today Revenue',
          '\$${todayRevenue.toStringAsFixed(2)}',
          Icons.attach_money,
          AppTheme.accentColor,
        ),
        _buildStatCard(
          'Pending Orders',
          '$pendingOrders',
          Icons.pending_actions,
          AppTheme.warningColor,
        ),
        _buildStatCard(
          'Active Drivers',
          '$activeDrivers',
          Icons.delivery_dining,
          AppTheme.primaryColor,
        ),
        _buildStatCard(
          'Total Orders',
          '$totalOrders',
          Icons.receipt,
          Colors.blueAccent,
        ),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                value,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                title,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.white.withOpacity(0.6),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: [
        _buildActionButton(
          'Customers',
          Icons.person,
          Colors.tealAccent,
          () => Navigator.pushNamed(context, AppRoutes.customers),
        ),
        _buildActionButton(
          'Users',
          Icons.people,
          AppTheme.primaryColor,
          () => Navigator.pushNamed(context, AppRoutes.users),
        ),
        _buildActionButton(
          'Inventory',
          Icons.inventory_2,
          Colors.blueAccent,
          () => Navigator.pushNamed(context, AppRoutes.inventory),
        ),
        _buildActionButton(
          'Loyalty',
          Icons.card_giftcard,
          AppTheme.accentColor,
          () => Navigator.pushNamed(context, AppRoutes.loyalty),
        ),
        _buildActionButton(
          'Stats',
          Icons.bar_chart,
          Colors.purpleAccent,
          () => Navigator.pushNamed(context, AppRoutes.stats),
        ),
      ],
    );
  }

  Widget _buildActionButton(String title, IconData icon, Color color, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.cardDark,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              title,
              style: const TextStyle(fontSize: 12),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentActivity() {
    // Placeholder for recent activity
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          _buildActivityItem('New order #1234', 'Just now', Icons.shopping_bag, AppTheme.accentColor),
          const Divider(height: 24),
          _buildActivityItem('Driver assigned', '2 min ago', Icons.delivery_dining, AppTheme.primaryColor),
          const Divider(height: 24),
          _buildActivityItem('Low stock alert', '5 min ago', Icons.warning, AppTheme.warningColor),
        ],
      ),
    );
  }

  Widget _buildActivityItem(String title, String time, IconData icon, Color color) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: color, size: 20),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(title),
        ),
        Text(
          time,
          style: TextStyle(
            fontSize: 12,
            color: Colors.white.withOpacity(0.5),
          ),
        ),
      ],
    );
  }
}
