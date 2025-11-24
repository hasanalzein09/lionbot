import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:lionbot_mobile/app/modules/orders/views/orders_view.dart';
import 'package:lionbot_mobile/app/modules/login/views/login_view.dart';


void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'Lion Delivery',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        useMaterial3: true,
      ),
      initialRoute: '/login',
      getPages: [
        GetPage(name: '/login', page: () => LoginView()),
        GetPage(name: '/home', page: () => OrdersView()),
      ],
    );
  }
}
