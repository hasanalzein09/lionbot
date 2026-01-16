import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';
import '../../routes/app_routes.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});
  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _searchController = TextEditingController();
  List<dynamic> _results = [];
  bool _isSearching = false;

  Future<void> _search(String query) async {
    if (query.isEmpty) {
      setState(() => _results = []);
      return;
    }
    setState(() => _isSearching = true);
    try {
      final all = await ApiService().getRestaurants();
      final filtered = all.where((r) => (r['name'] ?? '').toString().toLowerCase().contains(query.toLowerCase())).toList();
      if (mounted) setState(() { _results = filtered; _isSearching = false; });
    } catch (e) {
      setState(() => _isSearching = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: TextField(
          controller: _searchController,
          autofocus: true,
          decoration: InputDecoration(
            hintText: 'search'.tr + '...',
            border: InputBorder.none,
            filled: false,
          ),
          onChanged: (v) => _search(v),
        ),
      ),
      body: _isSearching
          ? const Center(child: CircularProgressIndicator())
          : _results.isEmpty
              ? Center(child: Text(_searchController.text.isEmpty ? 'Start typing to search' : 'No results'))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _results.length,
                  itemBuilder: (context, index) {
                    final r = _results[index];
                    return ListTile(
                      leading: CircleAvatar(backgroundColor: AppTheme.primaryColor.withOpacity(0.2),
                        child: const Icon(Icons.restaurant, color: AppTheme.primaryColor)),
                      title: Text(r['name'] ?? ''),
                      onTap: () => Get.toNamed(AppRoutes.restaurant, arguments: r),
                    );
                  },
                ),
    );
  }
}
