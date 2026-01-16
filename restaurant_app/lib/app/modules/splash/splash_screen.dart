import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../core/theme/app_theme.dart';
import '../../routes/app_routes.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.elasticOut),
    );
    _controller.forward();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    await Future.delayed(const Duration(seconds: 2));
    const storage = FlutterSecureStorage();
    final token = await storage.read(key: 'token');
    
    if (mounted) {
      Navigator.pushReplacementNamed(
        context,
        token != null ? AppRoutes.home : AppRoutes.login,
      );
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      body: Center(
        child: ScaleTransition(
          scale: _scaleAnimation,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [AppTheme.primaryColor, AppTheme.primaryColor.withOpacity(0.7)],
                  ),
                  borderRadius: BorderRadius.circular(30),
                  boxShadow: [
                    BoxShadow(color: AppTheme.primaryColor.withOpacity(0.4), blurRadius: 30),
                  ],
                ),
                child: const Icon(Icons.restaurant_menu, size: 60, color: Colors.white),
              ),
              const SizedBox(height: 24),
              const Text(
                'LION RESTAURANT',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, letterSpacing: 3),
              ),
              const SizedBox(height: 8),
              Text(
                'Order Management System',
                style: TextStyle(fontSize: 14, color: Colors.white.withOpacity(0.6)),
              ),
              const SizedBox(height: 48),
              CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation(AppTheme.primaryColor.withOpacity(0.8)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
