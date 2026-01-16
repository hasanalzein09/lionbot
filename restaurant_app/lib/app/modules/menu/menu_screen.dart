import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class MenuScreen extends StatelessWidget {
  const MenuScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Menu Management'),
        actions: [
          IconButton(icon: const Icon(Icons.add), onPressed: () {}),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildCategorySection('Burgers', [
            _buildMenuItem('Classic Burger', '\$12.99', true),
            _buildMenuItem('Cheese Burger', '\$14.99', true),
            _buildMenuItem('Double Burger', '\$18.99', false),
          ]),
          const SizedBox(height: 16),
          _buildCategorySection('Sides', [
            _buildMenuItem('French Fries', '\$4.99', true),
            _buildMenuItem('Onion Rings', '\$5.99', true),
          ]),
          const SizedBox(height: 16),
          _buildCategorySection('Drinks', [
            _buildMenuItem('Coca Cola', '\$2.99', true),
            _buildMenuItem('Fresh Juice', '\$4.99', true),
          ]),
        ],
      ),
    );
  }

  Widget _buildCategorySection(String title, List<Widget> items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            TextButton(onPressed: () {}, child: const Text('Edit')),
          ],
        ),
        const SizedBox(height: 8),
        ...items,
      ],
    );
  }

  Widget _buildMenuItem(String name, String price, bool available) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Container(
            width: 50, height: 50,
            decoration: BoxDecoration(
              color: AppTheme.surfaceDark,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.fastfood, color: AppTheme.primaryColor),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: const TextStyle(fontWeight: FontWeight.w500)),
                Text(price, style: const TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
          Switch(
            value: available,
            onChanged: (v) {},
            activeColor: AppTheme.accentColor,
          ),
        ],
      ),
    );
  }
}
