import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';
import '../../core/services/notification_service.dart';
import '../../routes/app_routes.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  Map<String, dynamic>? _settings;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    try {
      final settings = await ApiService().getSettings();
      if (mounted) setState(() { _settings = settings; _isLoading = false; });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _logout() async {
    NotificationService().stopPolling();
    await const FlutterSecureStorage().delete(key: 'token');
    if (mounted) {
      Navigator.pushNamedAndRemoveUntil(context, AppRoutes.login, (route) => false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryColor))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Business Settings
                  const Text('Business Settings', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                  const SizedBox(height: 12),
                  _buildSettingCard('Delivery Fee', '\$${_settings?['default_delivery_fee'] ?? 0}', Icons.delivery_dining),
                  _buildSettingCard('Min Order', '\$${_settings?['min_order_amount'] ?? 0}', Icons.shopping_cart),
                  _buildSettingCard('Max Radius', '${_settings?['max_delivery_radius_km'] ?? 0} km', Icons.map),
                  
                  const SizedBox(height: 24),
                  
                  // App Settings
                  const Text('App Settings', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                  const SizedBox(height: 12),
                  _buildToggleSetting('Push Notifications', true, (v) {}),
                  _buildToggleSetting('Dark Mode', true, (v) {}),
                  _buildToggleSetting('Auto-refresh', true, (v) {}),
                  
                  const SizedBox(height: 24),
                  
                  // Danger Zone
                  const Text('Account', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                  const SizedBox(height: 12),
                  Container(
                    decoration: BoxDecoration(
                      color: AppTheme.cardDark,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: ListTile(
                      leading: const Icon(Icons.logout, color: AppTheme.errorColor),
                      title: const Text('Logout', style: TextStyle(color: AppTheme.errorColor)),
                      onTap: () => showDialog(
                        context: context,
                        builder: (context) => AlertDialog(
                          backgroundColor: AppTheme.cardDark,
                          title: const Text('Logout'),
                          content: const Text('Are you sure you want to logout?'),
                          actions: [
                            TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
                            TextButton(onPressed: () { Navigator.pop(context); _logout(); }, 
                              child: const Text('Logout', style: TextStyle(color: AppTheme.errorColor))),
                          ],
                        ),
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 32),
                  
                  // Version
                  Center(
                    child: Text('Lion Admin v1.0.0', style: TextStyle(color: Colors.white.withOpacity(0.3), fontSize: 12)),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildSettingCard(String label, String value, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: AppTheme.cardDark, borderRadius: BorderRadius.circular(12)),
      child: Row(
        children: [
          Icon(icon, color: AppTheme.primaryColor),
          const SizedBox(width: 16),
          Expanded(child: Text(label)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildToggleSetting(String label, bool value, ValueChanged<bool> onChanged) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(color: AppTheme.cardDark, borderRadius: BorderRadius.circular(12)),
      child: SwitchListTile(
        title: Text(label),
        value: value,
        onChanged: onChanged,
        activeColor: AppTheme.primaryColor,
      ),
    );
  }
}
