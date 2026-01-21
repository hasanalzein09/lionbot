import '../config/app_config.dart';

/// Simple in-memory cache service with TTL support
class CacheService {
  static final CacheService _instance = CacheService._internal();
  factory CacheService() => _instance;
  CacheService._internal();

  final Map<String, _CacheEntry> _cache = {};

  /// Get default cache duration from config
  static Duration get defaultTTL => const Duration(minutes: AppConfig.cacheDurationMinutes);

  /// Get cached data if valid
  T? get<T>(String key) {
    final entry = _cache[key];
    if (entry == null) return null;

    // Check if expired
    if (DateTime.now().isAfter(entry.expiresAt)) {
      _cache.remove(key);
      return null;
    }

    return entry.data as T?;
  }

  /// Store data in cache with optional TTL
  void set<T>(String key, T data, {Duration? ttl}) {
    _cache[key] = _CacheEntry(
      data: data,
      expiresAt: DateTime.now().add(ttl ?? defaultTTL),
    );
  }

  /// Remove specific key from cache
  void remove(String key) {
    _cache.remove(key);
  }

  /// Remove all keys matching a prefix
  void removePrefix(String prefix) {
    _cache.removeWhere((key, _) => key.startsWith(prefix));
  }

  /// Clear all cached data
  void clear() {
    _cache.clear();
  }

  /// Clear expired entries
  void clearExpired() {
    final now = DateTime.now();
    _cache.removeWhere((_, entry) => now.isAfter(entry.expiresAt));
  }

  /// Check if key exists and is valid
  bool has(String key) {
    final entry = _cache[key];
    if (entry == null) return false;
    if (DateTime.now().isAfter(entry.expiresAt)) {
      _cache.remove(key);
      return false;
    }
    return true;
  }
}

class _CacheEntry {
  final dynamic data;
  final DateTime expiresAt;

  _CacheEntry({required this.data, required this.expiresAt});
}

/// Cache keys constants
class CacheKeys {
  static const String restaurants = 'restaurants';
  static const String restaurantCategories = 'restaurant_categories';
  static const String dashboardStats = 'dashboard_stats';
  static const String drivers = 'drivers';
  static const String settings = 'settings';

  static String restaurant(int id) => 'restaurant_$id';
  static String menu(int restaurantId) => 'menu_$restaurantId';
  static String orders(String? status) => 'orders_${status ?? 'all'}';
}
