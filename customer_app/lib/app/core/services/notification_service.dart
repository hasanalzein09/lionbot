import 'dart:async';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_core/firebase_core.dart';

@pragma('vm:entry-point')
Future<void> _firebaseBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
}

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final StreamController<RemoteMessage> _messageController = StreamController<RemoteMessage>.broadcast();
  
  String? _fcmToken;
  String? get fcmToken => _fcmToken;
  Stream<RemoteMessage> get onMessage => _messageController.stream;

  Future<void> init() async {
    FirebaseMessaging.onBackgroundMessage(_firebaseBackgroundHandler);
    
    await _messaging.requestPermission(alert: true, badge: true, sound: true);
    
    _fcmToken = await _messaging.getToken();
    _messaging.onTokenRefresh.listen((token) => _fcmToken = token);
    
    FirebaseMessaging.onMessage.listen((message) {
      _messageController.add(message);
    });
  }

  Future<void> subscribeToUser(int userId) async {
    await _messaging.subscribeToTopic('user_$userId');
  }
}
