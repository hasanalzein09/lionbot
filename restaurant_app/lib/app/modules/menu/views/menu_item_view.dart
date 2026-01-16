import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../controllers/menu_controller.dart';

class MenuItemView extends GetView<MenuManagementController> {
  const MenuItemView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل الصنف'),
      ),
      body: const Center(
        child: Text('صفحة تفاصيل الصنف'),
      ),
    );
  }
}
