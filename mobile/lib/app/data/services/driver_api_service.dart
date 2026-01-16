import 'package:dio/dio.dart';
import 'api_service.dart';

class DriverApiService {
  final _api = ApiService().client;

  Future<Response> updateLocation(int driverId, double lat, double lng) async {
    return await _api.patch(
      '/users/drivers/$driverId/location',
      data: {
        'latitude': lat,
        'longitude': lng,
      },
    );
  }

  Future<Response> updateStatus(int driverId, bool isActive) async {
    return await _api.patch(
      '/users/drivers/$driverId/status',
      data: {
        'is_active': isActive,
      },
    );
  }

  Future<List<dynamic>> getMyDeliveries(int driverId) async {
    final response = await _api.get('/orders/driver/$driverId');
    return response.data;
  }

  Future<Response> updateOrderStatus(int orderId, String status) async {
    return await _api.patch(
      '/orders/$orderId/status',
      data: {
        'status': status,
      },
    );
  }
}
