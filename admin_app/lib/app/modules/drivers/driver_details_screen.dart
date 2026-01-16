import 'package:flutter/material.dart';

class DriverDetailsScreen extends StatelessWidget {
  final int? driverId;

  const DriverDetailsScreen({super.key, this.driverId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل السائق'),
      ),
      body: Center(
        child: Text('Driver ID: ${driverId ?? "N/A"}'),
      ),
    );
  }
}
