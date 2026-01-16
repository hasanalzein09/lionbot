import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get/get.dart';
import 'dart:convert';
import '../constants/api_constants.dart';

class StorageService extends GetxService {
  final _storage = const FlutterSecureStorage();

  Future<void> saveToken(String token) async {
    await _storage.write(key: StorageKeys.token, value: token);
  }

  Future<String?> getToken() async {
    return await _storage.read(key: StorageKeys.token);
  }

  Future<void> saveUserId(int userId) async {
    await _storage.write(key: StorageKeys.userId, value: userId.toString());
  }

  Future<int?> getUserId() async {
    final id = await _storage.read(key: StorageKeys.userId);
    return id != null ? int.parse(id) : null;
  }

  Future<void> saveRestaurantId(int restaurantId) async {
    await _storage.write(key: StorageKeys.restaurantId, value: restaurantId.toString());
  }

  Future<int?> getRestaurantId() async {
    final id = await _storage.read(key: StorageKeys.restaurantId);
    return id != null ? int.parse(id) : null;
  }

  Future<void> saveUserData(Map<String, dynamic> userData) async {
    await _storage.write(key: StorageKeys.userData, value: jsonEncode(userData));
  }

  Future<Map<String, dynamic>?> getUserData() async {
    final data = await _storage.read(key: StorageKeys.userData);
    return data != null ? jsonDecode(data) : null;
  }

  Future<void> clearAll() async {
    await _storage.deleteAll();
  }

  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }
}
