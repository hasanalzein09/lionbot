import 'dart:async';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';

/// Background message handler
@pragma('vm:entry-point')
Future<void> _firebaseBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('🔔 Background notification: ${message.notification?.title}');
}

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final AudioPlayer _audioPlayer = AudioPlayer();
  final StreamController<RemoteMessage> _messageController = 
      StreamController<RemoteMessage>.broadcast();
  
  String? _fcmToken;
  
  String? get fcmToken => _fcmToken;
  Stream<RemoteMessage> get onMessage => _messageController.stream;

  Future<void> init() async {
    FirebaseMessaging.onBackgroundMessage(_firebaseBackgroundHandler);
    
    final settings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      criticalAlert: true,
      sound: true,
    );
    
    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      await _setupToken();
      _setupForegroundHandler();
    }
  }

  Future<void> _setupToken() async {
    _fcmToken = await _messaging.getToken();
    print('🔑 Restaurant FCM Token: $_fcmToken');
    
    _messaging.onTokenRefresh.listen((newToken) {
      _fcmToken = newToken;
    });
  }

  void _setupForegroundHandler() {
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('📬 New notification: ${message.notification?.title}');
      _messageController.add(message);
      _handleNotification(message);
    });

    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('👆 Notification tapped: ${message.data}');
    });
  }

  void _handleNotification(RemoteMessage message) {
    final type = message.data['type'] as String?;
    
    if (type == 'new_order') {
      // Play order alert sound
      _playOrderAlert();
    }
  }

  Future<void> _playOrderAlert() async {
    try {
      await _audioPlayer.play(AssetSource('sounds/order_alert.mp3'));
    } catch (e) {
      print('Audio error: $e');
    }
  }

  Future<void> subscribeToRestaurant(int restaurantId) async {
    await _messaging.subscribeToTopic('restaurant_$restaurantId');
    await _messaging.subscribeToTopic('restaurants');
    print('✅ Subscribed to restaurant_$restaurantId');
  }

  void dispose() {
    _messageController.close();
    _audioPlayer.dispose();
  }
}
