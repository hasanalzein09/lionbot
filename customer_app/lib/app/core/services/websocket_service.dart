import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// WebSocket service for real-time order tracking
class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  WebSocketService._internal();

  static const String wsBaseUrl = 'wss://lionbot-backend-426202982674.me-west1.run.app/ws';

  WebSocketChannel? _channel;
  Timer? _pingTimer;
  Timer? _reconnectTimer;
  bool _isConnected = false;
  int _reconnectAttempts = 0;
  static const int maxReconnectAttempts = 5;

  final _orderUpdateController = StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get orderUpdates => _orderUpdateController.stream;

  bool get isConnected => _isConnected;

  /// Connect to order tracking WebSocket
  Future<void> connectToOrderTracking(int orderId) async {
    await disconnect();
    
    try {
      _channel = WebSocketChannel.connect(Uri.parse('$wsBaseUrl/orders/$orderId'));
      _isConnected = true;
      _reconnectAttempts = 0;

      _channel!.stream.listen(
        (message) {
          _handleMessage(message);
        },
        onError: (error) {
          print('WebSocket error: $error');
          _handleDisconnect();
        },
        onDone: () {
          _handleDisconnect();
        },
      );

      // Start ping/pong for connection health
      _startPing();
    } catch (e) {
      print('WebSocket connect error: $e');
      _scheduleReconnect(orderId);
    }
  }

  void _handleMessage(dynamic message) {
    try {
      final data = json.decode(message);
      
      if (data['type'] == 'pong') {
        return; // Ping response
      }
      
      // Emit order update
      _orderUpdateController.add(data);
    } catch (e) {
      print('WebSocket message parse error: $e');
    }
  }

  void _startPing() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (_isConnected && _channel != null) {
        try {
          _channel!.sink.add(json.encode({'type': 'ping'}));
        } catch (e) {
          print('Ping error: $e');
        }
      }
    });
  }

  void _handleDisconnect() {
    _isConnected = false;
    _pingTimer?.cancel();
  }

  void _scheduleReconnect(int orderId) {
    if (_reconnectAttempts >= maxReconnectAttempts) {
      print('Max reconnect attempts reached');
      return;
    }

    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(
      Duration(seconds: (2 << _reconnectAttempts).clamp(1, 30)),
      () {
        _reconnectAttempts++;
        connectToOrderTracking(orderId);
      },
    );
  }

  /// Send message through WebSocket
  void send(Map<String, dynamic> message) {
    if (_isConnected && _channel != null) {
      _channel!.sink.add(json.encode(message));
    }
  }

  /// Disconnect from WebSocket
  Future<void> disconnect() async {
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _isConnected = false;

    if (_channel != null) {
      await _channel!.sink.close();
      _channel = null;
    }
  }

  void dispose() {
    disconnect();
    _orderUpdateController.close();
  }
}

// Riverpod Provider
final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  return WebSocketService();
});

// Order tracking stream provider
final orderTrackingProvider = StreamProvider.family<Map<String, dynamic>, int>((ref, orderId) {
  final wsService = ref.watch(webSocketServiceProvider);
  wsService.connectToOrderTracking(orderId);
  
  ref.onDispose(() {
    wsService.disconnect();
  });
  
  return wsService.orderUpdates;
});
