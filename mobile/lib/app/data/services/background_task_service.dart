import 'package:workmanager/workmanager.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lionbot_mobile/app/data/services/driver_api_service.dart';
import 'package:geolocator/geolocator.dart';

/// Background task identifiers
class BackgroundTasks {
  static const String locationUpdate = 'location_update_task';
  static const String syncOrders = 'sync_orders_task';
  static const String checkNewDeliveries = 'check_new_deliveries_task';
}

/// Top-level callback dispatcher (required by WorkManager)
@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((taskName, inputData) async {
    switch (taskName) {
      case BackgroundTasks.locationUpdate:
        await _updateLocationInBackground(inputData);
        break;
      case BackgroundTasks.syncOrders:
        await _syncOrdersInBackground();
        break;
      case BackgroundTasks.checkNewDeliveries:
        await _checkNewDeliveriesInBackground();
        break;
    }
    return Future.value(true);
  });
}

/// Update driver location in background
Future<void> _updateLocationInBackground(Map<String, dynamic>? inputData) async {
  try {
    final position = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );
    
    final driverId = inputData?['driver_id'] as int?;
    if (driverId != null) {
      final api = DriverApiService();
      await api.updateLocation(driverId, position.latitude, position.longitude);
    }
  } catch (e) {
    print('Background location update failed: $e');
  }
}

/// Sync pending orders in background
Future<void> _syncOrdersInBackground() async {
  // TODO: Implement order sync logic
  print('Syncing orders in background...');
}

/// Check for new deliveries
Future<void> _checkNewDeliveriesInBackground() async {
  // TODO: Implement delivery check and show notification
  print('Checking for new deliveries...');
}

/// Background Task Service
class BackgroundTaskService {
  bool _isInitialized = false;

  /// Initialize Workmanager
  Future<void> init() async {
    if (_isInitialized) return;
    
    await Workmanager().initialize(
      callbackDispatcher,
      isInDebugMode: false, // Set to true for debugging
    );
    
    _isInitialized = true;
  }

  /// Register periodic location updates (for active drivers)
  Future<void> startLocationTracking(int driverId) async {
    await init();
    
    await Workmanager().registerPeriodicTask(
      BackgroundTasks.locationUpdate,
      BackgroundTasks.locationUpdate,
      frequency: const Duration(minutes: 15), // Minimum on Android
      constraints: Constraints(
        networkType: NetworkType.connected,
        requiresBatteryNotLow: true,
      ),
      inputData: {'driver_id': driverId},
      existingWorkPolicy: ExistingWorkPolicy.replace,
    );
  }

  /// Stop location tracking
  Future<void> stopLocationTracking() async {
    await Workmanager().cancelByUniqueName(BackgroundTasks.locationUpdate);
  }

  /// Register order sync task
  Future<void> startOrderSync() async {
    await init();
    
    await Workmanager().registerPeriodicTask(
      BackgroundTasks.syncOrders,
      BackgroundTasks.syncOrders,
      frequency: const Duration(hours: 1),
      constraints: Constraints(
        networkType: NetworkType.connected,
      ),
      existingWorkPolicy: ExistingWorkPolicy.keep,
    );
  }

  /// One-time delivery check
  Future<void> checkForNewDeliveries() async {
    await init();
    
    await Workmanager().registerOneOffTask(
      '${BackgroundTasks.checkNewDeliveries}_${DateTime.now().millisecondsSinceEpoch}',
      BackgroundTasks.checkNewDeliveries,
      constraints: Constraints(
        networkType: NetworkType.connected,
      ),
    );
  }

  /// Cancel all background tasks
  Future<void> cancelAll() async {
    await Workmanager().cancelAll();
  }
}

/// Riverpod provider
final backgroundTaskProvider = Provider<BackgroundTaskService>((ref) {
  return BackgroundTaskService();
});
