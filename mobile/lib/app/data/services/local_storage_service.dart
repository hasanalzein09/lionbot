import 'package:hive_flutter/hive_flutter.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Offline-first local storage service using Hive
class LocalStorageService {
  static const String _ordersBox = 'orders_cache';
  static const String _userBox = 'user_data';
  static const String _settingsBox = 'app_settings';

  late Box<Map> _ordersCache;
  late Box<Map> _userCache;
  late Box<dynamic> _settingsCache;

  /// Initialize Hive and open boxes
  Future<void> init() async {
    await Hive.initFlutter();
    _ordersCache = await Hive.openBox<Map>(_ordersBox);
    _userCache = await Hive.openBox<Map>(_userBox);
    _settingsCache = await Hive.openBox<dynamic>(_settingsBox);
  }

  // ==================== Orders Cache ====================
  
  Future<void> cacheOrders(List<Map<String, dynamic>> orders) async {
    await _ordersCache.clear();
    for (var order in orders) {
      await _ordersCache.put(order['id'].toString(), order);
    }
  }

  List<Map<String, dynamic>> getCachedOrders() {
    return _ordersCache.values.map((e) => Map<String, dynamic>.from(e)).toList();
  }

  Future<void> cacheOrder(Map<String, dynamic> order) async {
    await _ordersCache.put(order['id'].toString(), order);
  }

  Map<String, dynamic>? getCachedOrder(int orderId) {
    final order = _ordersCache.get(orderId.toString());
    return order != null ? Map<String, dynamic>.from(order) : null;
  }

  // ==================== User Cache ====================
  
  Future<void> cacheUser(Map<String, dynamic> user) async {
    await _userCache.put('current_user', user);
  }

  Map<String, dynamic>? getCachedUser() {
    final user = _userCache.get('current_user');
    return user != null ? Map<String, dynamic>.from(user) : null;
  }

  Future<void> clearUserCache() async {
    await _userCache.clear();
  }

  // ==================== Settings Cache ====================
  
  Future<void> setSetting(String key, dynamic value) async {
    await _settingsCache.put(key, value);
  }

  T? getSetting<T>(String key, {T? defaultValue}) {
    return _settingsCache.get(key, defaultValue: defaultValue) as T?;
  }

  bool get isFirstLaunch => getSetting<bool>('first_launch', defaultValue: true) ?? true;
  
  Future<void> markFirstLaunchComplete() async {
    await setSetting('first_launch', false);
  }

  String? get lastLoginPhone => getSetting<String>('last_login_phone');
  
  Future<void> setLastLoginPhone(String phone) async {
    await setSetting('last_login_phone', phone);
  }

  // ==================== Cleanup ====================
  
  Future<void> clearAll() async {
    await _ordersCache.clear();
    await _userCache.clear();
    // Don't clear settings on logout
  }
}

/// Riverpod provider for local storage
final localStorageProvider = Provider<LocalStorageService>((ref) {
  return LocalStorageService();
});
