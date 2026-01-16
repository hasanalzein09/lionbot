import 'package:flutter/material.dart';

class OrderDetailsScreen extends StatelessWidget {
  final int? orderId;
  const OrderDetailsScreen({super.key, this.orderId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Order #$orderId')),
      body: const Center(child: Text('Order Details Screen')),
    );
  }
}
