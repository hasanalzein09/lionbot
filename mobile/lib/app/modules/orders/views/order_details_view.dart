import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import '../controllers/order_details_controller.dart';

class OrderDetailsView extends StatelessWidget {
  final OrderDetailsController controller = Get.put(OrderDetailsController());

  OrderDetailsView({super.key});

  @override
  Widget build(BuildContext context) {
    final order = controller.order;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text('Order #${order['id']}', style: const TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0,
      ),
      body: Column(
        children: [
          // Map View (Top Half)
          Expanded(
            flex: 4,
            child: Obx(() => GoogleMap(
              initialCameraPosition: CameraPosition(
                target: LatLng(
                  order['delivery_latitude'] ?? 0.0,
                  order['delivery_longitude'] ?? 0.0,
                ),
                zoom: 15,
              ),
              onMapCreated: (mapController) => controller.mapController = mapController,
              markers: controller.markers.value,
              myLocationEnabled: true,
              zoomControlsEnabled: false,
            )),
          ),
          
          // Order Info (Bottom Half)
          Expanded(
            flex: 6,
            child: Container(
              padding: const EdgeInsets.all(24),
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
                boxShadow: [
                  BoxShadow(color: Colors.black12, blurRadius: 20, offset: Offset(0, -5)),
                ],
              ),
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Status & Amount
                    Row(
                      mainAxisAlignment: MainAxisAlignment.between,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('TOTAL AMOUNT', style: TextStyle(color: Colors.grey, fontSize: 12)),
                            Text('\$${order['total_amount']}', 
                                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.blue.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            order['status'].toUpperCase(),
                            style: const TextStyle(color: Colors.blue, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 32),
                    
                    // Customer Details
                    const Text('CUSTOMER', style: TextStyle(color: Colors.grey, fontSize: 12)),
                    const SizedBox(height: 8),
                    ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: CircleAvatar(backgroundColor: Colors.grey[200], child: const Icon(Icons.person)),
                      title: Text(order['user_name'] ?? 'Guest Customer', style: const TextStyle(fontWeight: FontWeight.bold)),
                      subtitle: Text(order['user_phone'] ?? 'No Phone'),
                      trailing: IconButton(
                        icon: const Icon(Icons.phone, color: Colors.green),
                        onPressed: () {}, // Launch caller
                      ),
                    ),
                    const SizedBox(height: 24),
                    
                    // Address
                    const Text('DELIVERY ADDRESS', style: TextStyle(color: Colors.grey, fontSize: 12)),
                    const SizedBox(height: 8),
                    Text(order['delivery_address'] ?? 'No address provided', 
                        style: const TextStyle(fontSize: 16)),
                    const SizedBox(height: 32),
                    
                    // Deliver Button
                    Obx(() => SizedBox(
                      height: 60,
                      child: ElevatedButton(
                        onPressed: controller.isLoading.value ? null : controller.markAsDelivered,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          elevation: 0,
                        ),
                        child: controller.isLoading.value 
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text('CONFIRM DELIVERY', 
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      ),
                    )),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
