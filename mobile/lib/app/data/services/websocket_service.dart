import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

/// Real-time WebSocket service for instant order updates
class WebSocketService {
  static const String _baseUrl = 'wss://lionbot-backend-426202982674.me-west1.run.app/api/v1';
  
  WebSocketChannel? _channel;
  StreamController<Map<String, dynamic>>? _messageController;
  Timer? _pingTimer;
  Timer? _reconnectTimer;
  bool _isConnected = false;
  String? _currentEndpoint;
  
  Stream<Map<String, dynamic>> get messages => 
      _messageController?.stream ?? const Stream.empty();
  
  bool get isConnected => _isConnected;

  /// Connect as a driver to receive new order notifications
  Future<void> connectAsDriver(int driverId) async {
    await _connect('$_baseUrl/ws/driver/$driverId');
  }

  /// Connect as a restaurant to receive order updates
  Future<void> connectAsRestaurant(int restaurantId) async {
    await _connect('$_baseUrl/ws/restaurant/$restaurantId');
  }

  /// Connect to track a specific order
  Future<void> trackOrder(int orderId) async {
    await _connect('$_baseUrl/ws/order/$orderId');
  }

  Future<void> _connect(String endpoint) async {
    _currentEndpoint = endpoint;
    _messageController?.close();
    _messageController = StreamController<Map<String, dynamic>>.broadcast();
    
    try {
      _channel = WebSocketChannel.connect(Uri.parse(endpoint));
      _isConnected = true;
      
      // Start ping/pong to keep connection alive
      _startPingTimer();
      
      // Listen for messages
      _channel!.stream.listen(
        (data) {
          try {
            final message = jsonDecode(data as String) as Map<String, dynamic>;
            if (message['type'] != 'pong') {
              _messageController?.add(message);
            }
          } catch (e) {
            print('WebSocket parse error: $e');
          }
        },
        onError: (error) {
          print('WebSocket error: $error');
          _handleDisconnect();
        },
        onDone: () {
          _handleDisconnect();
        },
      );
    } catch (e) {
      print('WebSocket connection failed: $e');
      _scheduleReconnect();
    }
  }

  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (_isConnected && _channel != null) {
        _channel!.sink.add(jsonEncode({'type': 'ping'}));
      }
    });
  }

  void _handleDisconnect() {
    _isConnected = false;
    _pingTimer?.cancel();
    _scheduleReconnect();
  }

  void _scheduleReconnect() {
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 5), () {
      if (_currentEndpoint != null && !_isConnected) {
        _connect(_currentEndpoint!);
      }
    });
  }

  /// Send location update (for drivers)
  void sendLocationUpdate(double latitude, double longitude) {
    if (_isConnected && _channel != null) {
      _channel!.sink.add(jsonEncode({
        'type': 'location_update',
        'latitude': latitude,
        'longitude': longitude,
      }));
    }
  }

  void disconnect() {
    _isConnected = false;
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _messageController?.close();
    _currentEndpoint = null;
  }
}

/// Riverpod provider for WebSocket service
final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  final service = WebSocketService();
  ref.onDispose(() => service.disconnect());
  return service;
});

/// Stream provider for real-time order updates
final orderUpdatesProvider = StreamProvider<Map<String, dynamic>>((ref) {
  final service = ref.watch(webSocketServiceProvider);
  return service.messages;
});
