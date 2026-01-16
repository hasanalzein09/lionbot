import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:get/get.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:lionbot_mobile/app/modules/orders/views/orders_view.dart';
import 'package:lionbot_mobile/app/modules/login/views/login_view.dart';
import 'package:lionbot_mobile/app/modules/orders/views/order_details_view.dart';
import 'package:lionbot_mobile/app/data/services/local_storage_service.dart';
import 'package:lionbot_mobile/app/data/services/push_notification_service.dart';
import 'package:lionbot_mobile/app/data/services/websocket_service.dart';
import 'package:lionbot_mobile/app/core/localization/app_translations.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp();
  
  // Lock orientation to portrait
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  // Initialize Hive local storage
  final localStorage = LocalStorageService();
  await localStorage.init();
  
  // Initialize push notifications
  await PushNotificationService().init();
  
  // Set system UI style
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
  ));
  
  runApp(
    ProviderScope(
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'Lion Driver',
      debugShowCheckedModeBanner: false,
      
      // Localization - Arabic & English
      translations: AppTranslations(),
      locale: Get.deviceLocale ?? const Locale('en', 'US'),
      fallbackLocale: const Locale('en', 'US'),
      
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.amber,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        fontFamily: 'Roboto',
        appBarTheme: const AppBarTheme(
          elevation: 0,
          centerTitle: true,
          backgroundColor: Colors.white,
          foregroundColor: Colors.black,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            elevation: 0,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      ),
      initialRoute: '/login',
      getPages: [
        GetPage(name: '/login', page: () => LoginView()),
        GetPage(name: '/home', page: () => OrdersView()),
        GetPage(name: '/orders', page: () => OrdersView()),
        GetPage(name: '/order-details', page: () => OrderDetailsView()),
      ],
    );
  }
}
