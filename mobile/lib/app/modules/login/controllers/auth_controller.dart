import 'package:get/get.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:lionbot_mobile/app/data/services/api_service.dart';
import 'package:lionbot_mobile/app/data/services/location_service.dart';
import 'package:dio/dio.dart' as dio;

class AuthController extends GetxController {
  final _storage = const FlutterSecureStorage();
  final _api = ApiService().client;
  final _locationService = LocationService();

  var isLoading = false.obs;
  var currentUser = {}.obs;

  Future<void> login(String email, String password) async {
    isLoading.value = true;
    try {
      final formData = dio.FormData.fromMap({
        'username': email,
        'password': password,
        'grant_type': 'password',
      });

      final response = await _api.post(
        '/login/access-token',
        data: formData,
        options: dio.Options(contentType: dio.Headers.formUrlEncodedContentType),
      );

      final token = response.data['access_token'];
      await _storage.write(key: 'token', value: token);
      
      // Fetch user info
      final userResponse = await _api.get('/users/me');
      currentUser.value = userResponse.data;
      
      final int userId = userResponse.data['id'];
      final String role = userResponse.data['role'];

      if (role == 'driver') {
        // Start location tracking for drivers
        await _locationService.startTracking(userId);
        Get.offAllNamed('/orders'); // Driver dashboard
      } else {
        Get.offAllNamed('/home');
      }
      
      Get.snackbar('Success', 'Logged in successfully as ${role.toUpperCase()}');
    } catch (e) {
      Get.snackbar('Error', 'Login failed: ${e.toString()}');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> logout() async {
    _locationService.stopTracking();
    await _storage.delete(key: 'token');
    currentUser.value = {};
    Get.offAllNamed('/login');
  }
}
