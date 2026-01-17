import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:firebase_core/firebase_core.dart';

import 'app/core/theme/app_theme.dart';
import 'app/core/services/notification_service.dart';
import 'app/routes/app_routes.dart';

/// Global navigator key for accessing navigator from anywhere
final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

/// Handle navigation from notification tap
void _handleNotificationNavigation(String type, Map<String, dynamic> data) {
  final navigator = navigatorKey.currentState;
  if (navigator == null) return;

  switch (type) {
    case 'new_order':
    case 'order_update':
      final orderId = int.tryParse(data['order_id']?.toString() ?? '');
      if (orderId != null) {
        navigator.pushNamed(
          AppRoutes.orderDetails,
          arguments: {'orderId': orderId},
        );
      }
      break;
    default:
      // Navigate to orders list for unknown types
      navigator.pushNamed(AppRoutes.orders);
  }
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase
  await Firebase.initializeApp();

  // Initialize Hive for local storage
  await Hive.initFlutter();

  // Initialize notifications with FCM and navigation callback
  final notificationService = NotificationService();
  await notificationService.init();
  notificationService.setNavigationCallback(_handleNotificationNavigation);
  
  // Lock orientation (optional for desktop)
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);
  
  // Set system UI style
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
  ));
  
  runApp(
    const ProviderScope(
      child: LionAdminApp(),
    ),
  );
}

class LionAdminApp extends StatelessWidget {
  const LionAdminApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      navigatorKey: navigatorKey,
      title: 'Lion Admin',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.dark,
      initialRoute: AppRoutes.splash,
      onGenerateRoute: AppRoutes.generateRoute,
    );
  }
}
