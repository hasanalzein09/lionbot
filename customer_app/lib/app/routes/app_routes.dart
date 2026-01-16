import 'package:get/get.dart';

import '../modules/splash/splash_screen.dart';
import '../modules/auth/login_screen.dart';
import '../modules/auth/register_screen.dart';
import '../modules/home/home_screen.dart';
import '../modules/restaurant/restaurant_screen.dart';
import '../modules/cart/cart_screen.dart';
import '../modules/checkout/checkout_screen.dart';
import '../modules/orders/orders_screen.dart';
import '../modules/orders/order_tracking_screen.dart';
import '../modules/profile/profile_screen.dart';
import '../modules/search/search_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String home = '/home';
  static const String restaurant = '/restaurant';
  static const String cart = '/cart';
  static const String checkout = '/checkout';
  static const String orders = '/orders';
  static const String orderTracking = '/order-tracking';
  static const String profile = '/profile';
  static const String search = '/search';

  static List<GetPage> get routes => [
    GetPage(name: splash, page: () => const SplashScreen()),
    GetPage(name: login, page: () => const LoginScreen()),
    GetPage(name: register, page: () => const RegisterScreen()),
    GetPage(name: home, page: () => const HomeScreen()),
    GetPage(name: restaurant, page: () => const RestaurantScreen()),
    GetPage(name: cart, page: () => const CartScreen()),
    GetPage(name: checkout, page: () => const CheckoutScreen()),
    GetPage(name: orders, page: () => const OrdersScreen()),
    GetPage(name: orderTracking, page: () => const OrderTrackingScreen()),
    GetPage(name: profile, page: () => const ProfileScreen()),
    GetPage(name: search, page: () => const SearchScreen()),
  ];
}
