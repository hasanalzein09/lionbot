import 'package:get/get.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:lionbot_mobile/app/data/services/driver_api_service.dart';

class OrderDetailsController extends GetxController {
  final _driverApi = DriverApiService();
  var order = {}.obs;
  var isLoading = false.obs;
  
  // Map settings
  late GoogleMapController mapController;
  var markers = <Marker>{}.obs;

  @override
  void onInit() {
    super.onInit();
    order.value = Get.arguments;
    _updateMarkers();
  }

  void _updateMarkers() {
    if (order['delivery_latitude'] != null && order['delivery_longitude'] != null) {
      markers.add(
        Marker(
          markerId: const MarkerId('delivery_location'),
          position: LatLng(order['delivery_latitude'], order['delivery_longitude']),
          infoWindow: const InfoWindow(title: 'Delivery Location'),
        ),
      );
    }
  }

  Future<void> markAsDelivered() async {
    isLoading.value = true;
    try {
      await _driverApi.updateOrderStatus(order['id'], 'delivered');
      Get.snackbar('Success', 'Order delivered!');
      Get.back();
    } catch (e) {
      Get.snackbar('Error', 'Failed to update order');
    } finally {
      isLoading.value = false;
    }
  }
}
