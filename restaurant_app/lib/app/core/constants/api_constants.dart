class ApiConstants {
  // Base URL - Change this to your production URL
  // For local development use: http://10.0.2.2:8000 (Android emulator)
  // For real device use your computer's IP: http://192.168.x.x:8000
  static const String baseUrl = 'https://lionbot-backend-426202982674.me-west1.run.app';
  static const String apiVersion = '/api/v1';
  
  // Auth
  static const String login = '$apiVersion/login/access-token';
  static const String me = '$apiVersion/users/me';
  
  // Resources
  static const String restaurants = '$apiVersion/restaurants';
  static const String branches = '$apiVersion/branches';
  static const String menus = '$apiVersion/menus';
  static const String categories = '$apiVersion/menus/categories';
  static const String menuItems = '$apiVersion/menus/items';
  static const String orders = '$apiVersion/orders';
  static const String stats = '$apiVersion/stats';
}

class StorageKeys {
  static const String token = 'auth_token';
  static const String userId = 'user_id';
  static const String restaurantId = 'restaurant_id';
  static const String userData = 'user_data';
}
