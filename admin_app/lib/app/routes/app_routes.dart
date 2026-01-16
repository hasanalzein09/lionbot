import 'package:flutter/material.dart';

import '../modules/splash/splash_screen.dart';
import '../modules/auth/login_screen.dart';
import '../modules/home/home_screen.dart';
import '../modules/orders/orders_screen.dart';
import '../modules/orders/order_details_screen.dart';
import '../modules/restaurants/restaurants_screen.dart';
import '../modules/restaurants/restaurant_details_screen.dart';
import '../modules/restaurants/restaurant_form_screen.dart';
import '../modules/restaurants/menu_item_form_screen.dart';
import '../modules/drivers/drivers_screen.dart';
import '../modules/drivers/driver_details_screen.dart';
import '../modules/users/users_screen.dart';
import '../modules/customers/customers_screen.dart';
import '../modules/customers/customer_details_screen.dart';
import '../modules/inventory/inventory_screen.dart';
import '../modules/loyalty/loyalty_screen.dart';
import '../modules/settings/settings_screen.dart';
import '../modules/stats/stats_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String home = '/home';
  static const String orders = '/orders';
  static const String orderDetails = '/orders/details';
  static const String restaurants = '/restaurants';
  static const String restaurantDetails = '/restaurants/details';
  static const String restaurantForm = '/restaurants/form';
  static const String menuItemForm = '/restaurants/menu-item';
  static const String drivers = '/drivers';
  static const String driverDetails = '/drivers/details';
  static const String users = '/users';
  static const String customers = '/customers';
  static const String customerDetails = '/customers/details';
  static const String inventory = '/inventory';
  static const String loyalty = '/loyalty';
  static const String settings = '/settings';
  static const String stats = '/stats';

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

      case restaurants:
        return _buildRoute(const RestaurantsScreen());

      case restaurantDetails:
        final args = settings.arguments as Map<String, dynamic>?;
        return _buildRoute(RestaurantDetailsScreen(restaurantId: args?['restaurantId']));

      case restaurantForm:
        final args = settings.arguments as Map<String, dynamic>?;
        return _buildRoute(RestaurantFormScreen(restaurant: args?['restaurant']));

      case menuItemForm:
        final args = settings.arguments as Map<String, dynamic>?;
        return _buildRoute(MenuItemFormScreen(
          restaurantId: args?['restaurantId'],
          categoryId: args?['categoryId'],
          menuItem: args?['menuItem'],
        ));

      case drivers:
        return _buildRoute(const DriversScreen());

      case driverDetails:
        final args = settings.arguments as Map<String, dynamic>?;
        return _buildRoute(DriverDetailsScreen(driverId: args?['driverId']));

      case users:
        return _buildRoute(const UsersScreen());

      case customers:
        return _buildRoute(const CustomersScreen());

      case customerDetails:
        final args = settings.arguments as Map<String, dynamic>?;
        return _buildRoute(CustomerDetailsScreen(customer: args?['customer'] ?? {}));

      case inventory:
        return _buildRoute(const InventoryScreen());

      case loyalty:
        return _buildRoute(const LoyaltyScreen());

      case AppRoutes.settings:
        return _buildRoute(const SettingsScreen());

      case stats:
        return _buildRoute(const StatsScreen());

      default:
        return _buildRoute(const HomeScreen());
    }
  }

  static PageRouteBuilder _buildRoute(Widget page) {
    return PageRouteBuilder(
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return FadeTransition(
          opacity: animation,
          child: child,
        );
      },
      transitionDuration: const Duration(milliseconds: 200),
    );
  }
}
