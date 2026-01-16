import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'api_service.dart';
import '../config/app_config.dart';

/// Order notification model
class OrderNotification {
  final int orderId;
  final String status;
  final String customerName;
  final double total;
  final DateTime createdAt;

  OrderNotification({
    required this.orderId,
    required this.status,
    required this.customerName,
    required this.total,
    required this.createdAt,
  });

  factory OrderNotification.fromJson(Map<String, dynamic> json) {
    return OrderNotification(
      orderId: json['id'] ?? json['order_id'] ?? 0,
      status: json['status'] ?? 'new',
      customerName: json['customer_name'] ?? 'Customer',
      total: (json['total_amount'] ?? json['total'] ?? 0).toDouble(),
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
    );
  }
}

/// Background message handler (must be top-level function)
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  debugPrint('📬 Background message: ${message.messageId}');
}

/// Notification service with FCM + Polling fallback
class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();
  final AudioPlayer _audioPlayer = AudioPlayer();

  Timer? _pollingTimer;
  WebSocketChannel? _webSocket;
  String? _fcmToken;

  // Store stream subscriptions for proper cleanup
  StreamSubscription? _tokenRefreshSubscription;
  StreamSubscription? _foregroundMessageSubscription;
  StreamSubscription? _messageOpenedSubscription;
  StreamSubscription? _webSocketSubscription;

  final StreamController<OrderNotification> _orderController =
      StreamController<OrderNotification>.broadcast();
  final StreamController<int> _newOrderCountController =
      StreamController<int>.broadcast();

  int _lastOrderId = 0;
  int _newOrderCount = 0;

  Stream<OrderNotification> get onNewOrder => _orderController.stream;
  Stream<int> get onNewOrderCount => _newOrderCountController.stream;
  int get newOrderCount => _newOrderCount;
  String? get fcmToken => _fcmToken;

  /// Initialize notification service
  Future<void> init() async {
    debugPrint('🔔 NotificationService initializing...');

    try {
      // Initialize local notifications
      await _initLocalNotifications();

      // Request FCM permissions
      final settings = await _messaging.requestPermission(
        alert: true,
        badge: true,
        sound: true,
        criticalAlert: true,
      );

      if (settings.authorizationStatus == AuthorizationStatus.authorized) {
        debugPrint('✅ FCM permissions granted');

        // Get FCM token
        _fcmToken = await _messaging.getToken();
        debugPrint('📱 FCM Token: $_fcmToken');

        // Listen for token refresh (store subscription for cleanup)
        _tokenRefreshSubscription = _messaging.onTokenRefresh.listen((token) {
          _fcmToken = token;
          _registerTokenWithBackend();
        });

        // Set up message handlers
        _setupMessageHandlers();

        // Subscribe to admin topic
        await _messaging.subscribeToTopic(AppConfig.fcmOrdersTopic);
        debugPrint('📡 Subscribed to ${AppConfig.fcmOrdersTopic} topic');
      } else {
        debugPrint('⚠️ FCM permissions denied, using polling');
      }
    } catch (e) {
      debugPrint('❌ FCM init error: $e');
    }
  }

  /// Initialize local notifications
  Future<void> _initLocalNotifications() async {
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const settings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      settings,
      onDidReceiveNotificationResponse: (response) {
        debugPrint('Notification tapped: ${response.payload}');
        // Handle navigation to order details
      },
    );
  }

  /// Set up FCM message handlers
  void _setupMessageHandlers() {
    // Background handler
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

    // Foreground messages (store subscription for cleanup)
    _foregroundMessageSubscription = FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      debugPrint('📬 Foreground message: ${message.data}');
      _handleMessage(message);
    });

    // Message opened app (store subscription for cleanup)
    _messageOpenedSubscription = FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      debugPrint('📬 Message opened app: ${message.data}');
      _handleMessageTap(message);
    });

    // Check for initial message (app opened from notification)
    _messaging.getInitialMessage().then((message) {
      if (message != null) {
        debugPrint('📬 Initial message: ${message.data}');
        _handleMessageTap(message);
      }
    });
  }

  /// Handle incoming message
  void _handleMessage(RemoteMessage message) {
    final data = message.data;
    final type = data['type'] as String?;

    if (type == 'new_order') {
      // Play alert sound
      _playOrderAlert();

      // Show local notification
      _showLocalNotification(
        title: message.notification?.title ?? 'طلب جديد!',
        body: message.notification?.body ?? 'لديك طلب جديد',
        payload: jsonEncode(data),
      );

      // Add to stream
      final notification = OrderNotification(
        orderId: int.tryParse(data['order_id'] ?? '0') ?? 0,
        status: 'new',
        customerName: data['customer_name'] ?? 'Customer',
        total: double.tryParse(data['total'] ?? '0') ?? 0,
        createdAt: DateTime.now(),
      );

      _orderController.add(notification);
      _newOrderCount++;
      _newOrderCountController.add(_newOrderCount);
    }
  }

  /// Handle notification tap
  void _handleMessageTap(RemoteMessage message) {
    final data = message.data;
    final orderId = data['order_id'];

    if (orderId != null) {
      // Navigate to order details (handled by the app)
      debugPrint('Navigate to order: $orderId');
    }
  }

  /// Show local notification
  Future<void> _showLocalNotification({
    required String title,
    required String body,
    String? payload,
  }) async {
    final androidDetails = AndroidNotificationDetails(
      AppConfig.notificationChannelId,
      'Orders',
      channelDescription: 'New order notifications',
      importance: Importance.high,
      priority: Priority.high,
      playSound: true,
      enableVibration: true,
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _localNotifications.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title,
      body,
      details,
      payload: payload,
    );
  }

  /// Play order alert sound
  Future<void> _playOrderAlert() async {
    try {
      await _audioPlayer.play(AssetSource('sounds/order_alert.mp3'));
    } catch (e) {
      debugPrint('⚠️ Could not play sound: $e');
    }
  }

  /// Register FCM token with backend
  Future<void> _registerTokenWithBackend() async {
    if (_fcmToken == null) return;

    try {
      await ApiService().registerFcmToken(_fcmToken!);
      debugPrint('✅ FCM token registered with backend');
    } catch (e) {
      debugPrint('❌ Failed to register FCM token: $e');
    }
  }

  /// Start polling for new orders (fallback)
  void startPolling() {
    stopPolling();
    debugPrint('📡 Starting order polling...');

    // Register FCM token if available
    if (_fcmToken != null) {
      _registerTokenWithBackend();
    }

    // Poll at configured interval
    _pollingTimer = Timer.periodic(
      Duration(seconds: AppConfig.pollingIntervalSeconds),
      (_) => _checkNewOrders(),
    );

    // Initial check
    _checkNewOrders();
  }

  /// Stop polling
  void stopPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
  }

  /// Check for new orders
  Future<void> _checkNewOrders() async {
    try {
      final orders = await ApiService().getOrders(limit: 10, status: 'new');

      if (orders.isNotEmpty) {
        int newCount = 0;
        for (final order in orders) {
          final orderId = order['id'] as int? ?? 0;
          if (orderId > _lastOrderId) {
            newCount++;
            final notification = OrderNotification.fromJson(order);
            _orderController.add(notification);

            // Play sound for new orders
            if (newCount > 0) {
              _playOrderAlert();
            }

            debugPrint('🆕 New order #$orderId detected!');
          }
        }

        // Update last seen order ID
        final latestId = orders.first['id'] as int? ?? 0;
        if (latestId > _lastOrderId) {
          _lastOrderId = latestId;
        }

        // Update new order count
        _newOrderCount = orders.length;
        _newOrderCountController.add(_newOrderCount);
      }
    } catch (e) {
      debugPrint('❌ Polling error: $e');
    }
  }

  /// Mark orders as seen (reset count)
  void markOrdersSeen() {
    _newOrderCount = 0;
    _newOrderCountController.add(0);
  }

  /// Connect to WebSocket (for real-time support)
  void connectWebSocket(String url) {
    try {
      // Cancel existing subscription before reconnecting
      _webSocketSubscription?.cancel();

      _webSocket = WebSocketChannel.connect(Uri.parse(url));
      _webSocketSubscription = _webSocket!.stream.listen(
        (data) {
          final json = jsonDecode(data);
          if (json['type'] == 'new_order') {
            _playOrderAlert();
            final notification = OrderNotification.fromJson(json['data']);
            _orderController.add(notification);
            _newOrderCount++;
            _newOrderCountController.add(_newOrderCount);
          }
        },
        onError: (error) {
          debugPrint('WebSocket error: $error');
        },
        onDone: () {
          debugPrint('WebSocket closed');
          Future.delayed(const Duration(seconds: 5), () {
            connectWebSocket(url);
          });
        },
      );
    } catch (e) {
      debugPrint('WebSocket connection failed: $e');
    }
  }

  void dispose() {
    // Cancel all stream subscriptions to prevent memory leaks
    _tokenRefreshSubscription?.cancel();
    _foregroundMessageSubscription?.cancel();
    _messageOpenedSubscription?.cancel();
    _webSocketSubscription?.cancel();

    stopPolling();
    _webSocket?.sink.close();
    _orderController.close();
    _newOrderCountController.close();
    _audioPlayer.dispose();
  }
}

/// Provider for notification service
final notificationServiceProvider = Provider<NotificationService>((ref) {
  return NotificationService();
});

/// Stream provider for new orders
final newOrderStreamProvider = StreamProvider<OrderNotification>((ref) {
  return ref.watch(notificationServiceProvider).onNewOrder;
});

/// Stream provider for new order count (for badge)
final newOrderCountProvider = StreamProvider<int>((ref) {
  return ref.watch(notificationServiceProvider).onNewOrderCount;
});
