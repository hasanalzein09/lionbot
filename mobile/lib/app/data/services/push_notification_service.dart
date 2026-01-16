import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Background message handler (must be top-level function)
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('Background message: ${message.messageId}');
}

/// Push Notification Service using Firebase Cloud Messaging
class PushNotificationService {
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  String? _fcmToken;

  String? get fcmToken => _fcmToken;

  /// Initialize Firebase and request permissions
  Future<void> init() async {
    // Initialize Firebase
    await Firebase.initializeApp();
    
    // Set background handler
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
    
    // Request permissions (iOS)
    final settings = await _messaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );
    
    print('Notification permission: ${settings.authorizationStatus}');
    
    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      await _setupToken();
      _setupForegroundHandler();
    }
  }

  Future<void> _setupToken() async {
    // Get FCM token
    _fcmToken = await _messaging.getToken();
    print('FCM Token: $_fcmToken');
    
    // Listen for token refresh
    _messaging.onTokenRefresh.listen((newToken) {
      _fcmToken = newToken;
      // TODO: Send to backend
      _sendTokenToServer(newToken);
    });
  }

  void _setupForegroundHandler() {
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('Foreground message: ${message.notification?.title}');
      
      // Handle different notification types
      final data = message.data;
      switch (data['type']) {
        case 'new_order':
          _handleNewOrderNotification(data);
          break;
        case 'order_update':
          _handleOrderUpdateNotification(data);
          break;
        case 'earnings':
          _handleEarningsNotification(data);
          break;
      }
    });

    // Handle notification tap when app is in background
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      _handleNotificationTap(message);
    });
  }

  void _handleNewOrderNotification(Map<String, dynamic> data) {
    // Show local notification or update UI
    print('New order available: ${data['order_id']}');
  }

  void _handleOrderUpdateNotification(Map<String, dynamic> data) {
    print('Order ${data['order_id']} updated to ${data['status']}');
  }

  void _handleEarningsNotification(Map<String, dynamic> data) {
    print('Earnings update: ${data['amount']}');
  }

  void _handleNotificationTap(RemoteMessage message) {
    final data = message.data;
    // Navigate to appropriate screen
    print('Notification tapped: ${data['type']}');
  }

  Future<void> _sendTokenToServer(String token) async {
    // TODO: Call API to register token
    print('Sending FCM token to server: $token');
  }

  /// Subscribe to topic for broadcasts
  Future<void> subscribeToTopic(String topic) async {
    await _messaging.subscribeToTopic(topic);
    print('Subscribed to topic: $topic');
  }

  /// Unsubscribe from topic
  Future<void> unsubscribeFromTopic(String topic) async {
    await _messaging.unsubscribeFromTopic(topic);
    print('Unsubscribed from topic: $topic');
  }
}

/// Riverpod provider
final pushNotificationProvider = Provider<PushNotificationService>((ref) {
  return PushNotificationService();
});
