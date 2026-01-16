/// Application Configuration
///
/// This file manages environment-specific configuration.
/// Values are passed at build time using --dart-define flags.
///
/// Example build command:
/// flutter build apk --dart-define=API_BASE_URL=https://your-api.com/api/v1
///
/// For development, create a .env file (not committed to git) with:
/// API_BASE_URL=https://your-api.com/api/v1
library app_config;

class AppConfig {
  // Singleton pattern
  static final AppConfig _instance = AppConfig._internal();
  factory AppConfig() => _instance;
  AppConfig._internal();

  /// API Base URL - passed via --dart-define at build time
  /// Default is empty to prevent accidental exposure
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: '',
  );

  /// Check if API is configured
  static bool get isConfigured => apiBaseUrl.isNotEmpty;

  /// Polling interval for notifications in seconds
  static const int pollingIntervalSeconds = int.fromEnvironment(
    'POLLING_INTERVAL',
    defaultValue: 15,
  );

  /// Enable debug logging
  static const bool debugMode = bool.fromEnvironment(
    'DEBUG_MODE',
    defaultValue: false,
  );

  /// FCM Topic for admin orders
  static const String fcmOrdersTopic = String.fromEnvironment(
    'FCM_ORDERS_TOPIC',
    defaultValue: 'admin_orders',
  );

  /// Notification channel ID
  static const String notificationChannelId = String.fromEnvironment(
    'NOTIFICATION_CHANNEL_ID',
    defaultValue: 'orders_channel',
  );

  /// Request timeout in seconds
  static const int requestTimeoutSeconds = int.fromEnvironment(
    'REQUEST_TIMEOUT',
    defaultValue: 30,
  );

  /// Maximum items per page for pagination
  static const int defaultPageSize = int.fromEnvironment(
    'DEFAULT_PAGE_SIZE',
    defaultValue: 50,
  );

  /// Max retry attempts for API calls
  static const int maxRetryAttempts = int.fromEnvironment(
    'MAX_RETRY_ATTEMPTS',
    defaultValue: 3,
  );

  /// Cache duration in minutes
  static const int cacheDurationMinutes = int.fromEnvironment(
    'CACHE_DURATION_MINUTES',
    defaultValue: 5,
  );

  /// WebSocket URL for real-time updates
  static const String webSocketUrl = String.fromEnvironment(
    'WEBSOCKET_URL',
    defaultValue: '',
  );

  /// Minimum password length for validation
  static const int minPasswordLength = int.fromEnvironment(
    'MIN_PASSWORD_LENGTH',
    defaultValue: 8,
  );

  /// App version for display
  static const String appVersion = String.fromEnvironment(
    'APP_VERSION',
    defaultValue: '1.0.0',
  );

  /// Whether to enable analytics
  static const bool enableAnalytics = bool.fromEnvironment(
    'ENABLE_ANALYTICS',
    defaultValue: true,
  );
}
