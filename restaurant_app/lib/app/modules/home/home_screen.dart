import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:badges/badges.dart' as badges;

import '../../core/theme/app_theme.dart';
import '../../core/services/notification_service.dart';
import '../../routes/app_routes.dart';
import '../orders/orders_screen.dart';
import '../menu/menu_screen.dart';
import '../settings/settings_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _currentIndex = 0;
  int _newOrderCount = 0;

  final List<Widget> _screens = [
    const DashboardTab(),
    const OrdersScreen(),
    const MenuScreen(),
    const SettingsScreen(),
  ];

  @override
  void initState() {
    super.initState();
    _listenToOrders();
  }

  void _listenToOrders() {
    NotificationService().onMessage.listen((message) {
      if (message.data['type'] == 'new_order') {
        setState(() => _newOrderCount++);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: AppTheme.cardDark,
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.3), blurRadius: 10)],
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildNavItem(0, Icons.dashboard_rounded, 'Dashboard'),
                _buildNavItem(1, Icons.receipt_long_rounded, 'Orders', badge: _newOrderCount),
                _buildNavItem(2, Icons.restaurant_menu_rounded, 'Menu'),
                _buildNavItem(3, Icons.settings_rounded, 'Settings'),
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
      onTap: () {
        setState(() {
          _currentIndex = index;
          if (index == 1) _newOrderCount = 0;
        });
      },
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
                    badgeContent: Text(badge > 9 ? '9+' : badge.toString(),
                      style: const TextStyle(color: Colors.white, fontSize: 10)),
                    badgeStyle: const badges.BadgeStyle(badgeColor: AppTheme.errorColor),
                    child: Icon(icon, color: isSelected ? AppTheme.primaryColor : AppTheme.textMuted),
                  )
                : Icon(icon, color: isSelected ? AppTheme.primaryColor : AppTheme.textMuted),
            const SizedBox(height: 4),
            Text(label, style: TextStyle(
              fontSize: 11,
              color: isSelected ? AppTheme.primaryColor : AppTheme.textMuted,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
            )),
          ],
        ),
      ),
    );
  }
}

// Dashboard Tab
class DashboardTab extends StatelessWidget {
  const DashboardTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Dashboard')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Today's Stats
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 1.5,
              children: [
                _buildStatCard('New Orders', '5', Icons.fiber_new, AppTheme.primaryColor),
                _buildStatCard('Preparing', '3', Icons.restaurant, Colors.blueAccent),
                _buildStatCard('Ready', '2', Icons.check_circle, AppTheme.accentColor),
                _buildStatCard("Today's Revenue", '\$245', Icons.attach_money, AppTheme.warningColor),
              ],
            ),
            const SizedBox(height: 24),
            
            // Quick Actions
            const Text('Quick Actions', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: _buildActionButton(context, 'View Orders', Icons.list_alt, AppTheme.primaryColor,
                    () => Navigator.pushNamed(context, AppRoutes.orders))),
                const SizedBox(width: 12),
                Expanded(child: _buildActionButton(context, 'Edit Menu', Icons.menu_book, Colors.blueAccent,
                    () => Navigator.pushNamed(context, AppRoutes.menu))),
              ],
            ),
          ],
        ),
      ),
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
          Icon(icon, color: color),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(value, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              Text(title, style: TextStyle(fontSize: 12, color: Colors.white.withOpacity(0.6))),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton(BuildContext context, String title, IconData icon, Color color, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(color: AppTheme.cardDark, borderRadius: BorderRadius.circular(12)),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(title, style: const TextStyle(fontSize: 13)),
          ],
        ),
      ),
    );
  }
}
