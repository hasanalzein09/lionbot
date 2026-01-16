import 'dart:async';
import 'package:geolocator/geolocator.dart';
import 'driver_api_service.dart';

class LocationService {
  static final LocationService _instance = LocationService._internal();
  factory LocationService() => _instance;
  LocationService._internal();

  final _driverApi = DriverApiService();
  StreamSubscription<Position>? _positionStream;
  int? _currentDriverId;

  Future<void> startTracking(int driverId) async {
    _currentDriverId = driverId;
    
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }

    _positionStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 50, // Update every 50 meters
      ),
    ).listen((Position position) {
      _updateLocationOnServer(position);
    });
  }

  void stopTracking() {
    _positionStream?.cancel();
    _positionStream = null;
  }

  Future<void> _updateLocationOnServer(Position position) async {
    if (_currentDriverId == null) return;
    try {
      await _driverApi.updateLocation(
        _currentDriverId!,
        position.latitude,
        position.longitude,
      );
    } catch (e) {
      print('Failed to update location to server: $e');
    }
  }
}
