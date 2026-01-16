import 'package:flutter/material.dart';

import '../modules/splash/splash_screen.dart';
import '../modules/auth/login_screen.dart';
import '../modules/home/home_screen.dart';
import '../modules/orders/orders_screen.dart';
import '../modules/orders/order_details_screen.dart';
import '../modules/menu/menu_screen.dart';
import '../modules/settings/settings_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String home = '/home';
  static const String orders = '/orders';
  static const String orderDetails = '/orders/details';
  static const String menu = '/menu';
  static const String settings = '/settings';

  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case splash:
        return _buildRoute(const SplashScreen());
      
      case login:
        return _buildRoute(const LoginScreen());
      
      case home:
        return _buildRoute(const HomeScreen());
      
      case orders:
        return _buildRoute(const OrdersScreen());
      
      case orderDetails:
        final args = settings.arguments as Map<String, dynamic>?;
        return _buildRoute(OrderDetailsScreen(orderId: args?['orderId']));
      
      case menu:
        return _buildRoute(const MenuScreen());
      
      case AppRoutes.settings:
        return _buildRoute(const SettingsScreen());
      
      default:
        return _buildRoute(const HomeScreen());
    }
  }

  static PageRouteBuilder _buildRoute(Widget page) {
    return PageRouteBuilder(
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return FadeTransition(opacity: animation, child: child);
      },
      transitionDuration: const Duration(milliseconds: 200),
    );
  }
}
