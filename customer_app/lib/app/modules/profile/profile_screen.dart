import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get/get.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';
import '../../routes/app_routes.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _user;
  Map<String, dynamic>? _loyalty;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final user = await ApiService().getCurrentUser();
      final loyalty = await ApiService().getLoyaltyStatus();
      if (mounted) setState(() { _user = user; _loyalty = loyalty; });
    } catch (e) {}
  }

  Future<void> _logout() async {
    await const FlutterSecureStorage().deleteAll();
    Get.offAllNamed(AppRoutes.login);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('profile'.tr)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Profile Header
            CircleAvatar(radius: 50, backgroundColor: AppTheme.primaryColor.withOpacity(0.2),
              child: Text(_user?['full_name']?[0] ?? 'U', style: const TextStyle(fontSize: 36, fontWeight: FontWeight.bold))),
            const SizedBox(height: 16),
            Text(_user?['full_name'] ?? 'User', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            Text(_user?['phone_number'] ?? '', style: TextStyle(color: Colors.grey[600])),
            const SizedBox(height: 24),
            
            // Loyalty Card
            if (_loyalty != null)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(colors: [AppTheme.primaryColor, AppTheme.secondaryColor]),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.stars, color: Colors.white, size: 40),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('${_loyalty!['total_points'] ?? 0} ${'points'.tr}',
                            style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
                          Text((_loyalty!['tier'] ?? 'Bronze').toString().toUpperCase(),
                            style: const TextStyle(color: Colors.white70)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            const SizedBox(height: 24),
            
            // Menu Items
            _buildMenuItem(Icons.person_outline, 'edit_profile'.tr, () {}),
            _buildMenuItem(Icons.location_on_outlined, 'addresses'.tr, () {}),
            _buildMenuItem(Icons.card_giftcard, 'rewards'.tr, () {}),
            _buildMenuItem(Icons.language, 'language'.tr, () => _showLanguageDialog()),
            _buildMenuItem(Icons.settings_outlined, 'settings'.tr, () {}),
            const Divider(height: 32),
            _buildMenuItem(Icons.logout, 'logout'.tr, () => _showLogoutDialog(), color: Colors.red),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuItem(IconData icon, String title, VoidCallback onTap, {Color? color}) {
    return ListTile(
      leading: Icon(icon, color: color ?? AppTheme.primaryColor),
      title: Text(title, style: TextStyle(color: color)),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }

  void _showLanguageDialog() {
    Get.dialog(AlertDialog(
      title: Text('language'.tr),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ListTile(title: const Text('English'), onTap: () { Get.updateLocale(const Locale('en', 'US')); Get.back(); }),
          ListTile(title: const Text('العربية'), onTap: () { Get.updateLocale(const Locale('ar', 'SA')); Get.back(); }),
        ],
      ),
    ));
  }

  void _showLogoutDialog() {
    Get.dialog(AlertDialog(
      title: Text('logout'.tr),
      content: const Text('Are you sure?'),
      actions: [
        TextButton(onPressed: () => Get.back(), child: Text('cancel'.tr)),
        TextButton(onPressed: () { Get.back(); _logout(); }, child: Text('logout'.tr, style: const TextStyle(color: Colors.red))),
      ],
    ));
  }
}
