import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/services/api_service.dart';
import '../../../core/services/storage_service.dart';
import '../../../routes/app_pages.dart';

class LoginController extends GetxController {
  final ApiService _api = Get.find<ApiService>();
  final StorageService _storage = Get.find<StorageService>();

  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  
  final isLoading = false.obs;
  final obscurePassword = true.obs;
  final errorMessage = ''.obs;

  @override
  void onClose() {
    emailController.dispose();
    passwordController.dispose();
    super.onClose();
  }

  void togglePasswordVisibility() {
    obscurePassword.value = !obscurePassword.value;
  }

  Future<void> login() async {
    if (emailController.text.isEmpty || passwordController.text.isEmpty) {
      errorMessage.value = 'الرجاء إدخال البريد الإلكتروني وكلمة المرور';
      return;
    }

    isLoading.value = true;
    errorMessage.value = '';

    try {
      final response = await _api.login(
        emailController.text.trim(),
        passwordController.text,
      );

      if (response.statusCode == 200) {
        final token = response.data['access_token'];
        await _storage.saveToken(token);

        // Get user info
        final userResponse = await _api.getMe();
        if (userResponse.statusCode == 200) {
          final userData = userResponse.data;
          await _storage.saveUserId(userData['id']);
          await _storage.saveUserData(userData);
          
          // Check if user has restaurant access
          if (userData['role'] == 'restaurant_manager' || userData['role'] == 'super_admin') {
            Get.offAllNamed(Routes.dashboard);
          } else {
            errorMessage.value = 'هذا الحساب غير مصرح له بالدخول';
            await _storage.clearAll();
          }
        }
      }
    } catch (e) {
      errorMessage.value = 'خطأ في تسجيل الدخول. تأكد من البيانات';
    } finally {
      isLoading.value = false;
    }
  }
}
