import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';
import '../../routes/app_routes.dart';

class RestaurantsScreen extends StatefulWidget {
  const RestaurantsScreen({super.key});

  @override
  State<RestaurantsScreen> createState() => _RestaurantsScreenState();
}

class _RestaurantsScreenState extends State<RestaurantsScreen> {
  List<dynamic> _restaurants = [];
  List<dynamic> _filteredRestaurants = [];
  List<dynamic> _categories = [];
  bool _isLoading = true;
  String _searchQuery = '';
  String _selectedCategory = 'all';
  String _selectedStatus = 'all';

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final results = await Future.wait([
        ApiService().getRestaurants(),
        ApiService().getRestaurantCategories(),
      ]);
      if (mounted) {
        setState(() {
          _restaurants = results[0];
          _categories = results[1];
          _applyFilters();
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
      _showError('فشل تحميل المطاعم');
    }
  }

  void _applyFilters() {
    _filteredRestaurants = _restaurants.where((r) {
      // Search filter
      if (_searchQuery.isNotEmpty) {
        final name = (r['name'] ?? '').toString().toLowerCase();
        final nameAr = (r['name_ar'] ?? '').toString().toLowerCase();
        final phone = (r['phone_number'] ?? '').toString().toLowerCase();
        final query = _searchQuery.toLowerCase();
        if (!name.contains(query) && !nameAr.contains(query) && !phone.contains(query)) {
          return false;
        }
      }

      // Category filter
      if (_selectedCategory != 'all') {
        final catId = r['category_id']?.toString();
        if (catId != _selectedCategory) return false;
      }

      // Status filter
      if (_selectedStatus != 'all') {
        final isActive = r['is_active'] == true;
        if (_selectedStatus == 'active' && !isActive) return false;
        if (_selectedStatus == 'inactive' && isActive) return false;
      }

      return true;
    }).toList();
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppTheme.errorColor),
    );
  }

  void _showSuccess(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppTheme.accentColor),
    );
  }

  Future<void> _deleteRestaurant(Map<String, dynamic> restaurant) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardDark,
        title: const Text('حذف المطعم'),
        content: Text('هل أنت متأكد من حذف "${restaurant['name']}"؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('إلغاء'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: AppTheme.errorColor),
            child: const Text('حذف'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await ApiService().deleteRestaurant(restaurant['id']);
        _showSuccess('تم حذف المطعم بنجاح');
        _loadData();
      } catch (e) {
        _showError('فشل حذف المطعم');
      }
    }
  }

  Future<void> _toggleRestaurantStatus(Map<String, dynamic> restaurant) async {
    try {
      final newStatus = !(restaurant['is_active'] == true);
      await ApiService().updateRestaurant(restaurant['id'], {'is_active': newStatus});
      _showSuccess(newStatus ? 'تم تفعيل المطعم' : 'تم تعطيل المطعم');
      _loadData();
    } catch (e) {
      _showError('فشل تحديث الحالة');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('المطاعم'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final result = await Navigator.pushNamed(
            context,
            AppRoutes.restaurantForm,
          );
          if (result == true) _loadData();
        },
        backgroundColor: AppTheme.primaryColor,
        icon: const Icon(Icons.add),
        label: const Text('إضافة مطعم'),
      ),
      body: Column(
        children: [
          // Search & Filters
          _buildFilters(),

          // Results count
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: [
                Text(
                  '${_filteredRestaurants.length} مطعم',
                  style: TextStyle(color: Colors.white.withOpacity(0.6)),
                ),
                const Spacer(),
                if (_searchQuery.isNotEmpty || _selectedCategory != 'all' || _selectedStatus != 'all')
                  TextButton(
                    onPressed: () {
                      setState(() {
                        _searchQuery = '';
                        _selectedCategory = 'all';
                        _selectedStatus = 'all';
                        _applyFilters();
                      });
                    },
                    child: const Text('مسح الفلاتر'),
                  ),
              ],
            ),
          ),

          // Restaurant List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryColor))
                : _filteredRestaurants.isEmpty
                    ? _buildEmptyState()
                    : RefreshIndicator(
                        onRefresh: _loadData,
                        child: ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _filteredRestaurants.length,
                          itemBuilder: (context, index) => _buildRestaurantCard(_filteredRestaurants[index]),
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilters() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        border: Border(bottom: BorderSide(color: Colors.white.withOpacity(0.1))),
      ),
      child: Column(
        children: [
          // Search bar
          TextField(
            onChanged: (value) {
              setState(() {
                _searchQuery = value;
                _applyFilters();
              });
            },
            decoration: InputDecoration(
              hintText: 'البحث عن مطعم...',
              prefixIcon: const Icon(Icons.search),
              suffixIcon: _searchQuery.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        setState(() {
                          _searchQuery = '';
                          _applyFilters();
                        });
                      },
                    )
                  : null,
              filled: true,
              fillColor: AppTheme.cardDark,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Filter chips
          Row(
            children: [
              // Category filter
              Expanded(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  decoration: BoxDecoration(
                    color: AppTheme.cardDark,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: _selectedCategory,
                      isExpanded: true,
                      dropdownColor: AppTheme.cardDark,
                      hint: const Text('التصنيف'),
                      items: [
                        const DropdownMenuItem(value: 'all', child: Text('كل التصنيفات')),
                        ..._categories.map((c) => DropdownMenuItem(
                          value: c['id'].toString(),
                          child: Text(c['name_ar'] ?? c['name'] ?? ''),
                        )),
                      ],
                      onChanged: (value) {
                        setState(() {
                          _selectedCategory = value ?? 'all';
                          _applyFilters();
                        });
                      },
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),

              // Status filter
              Expanded(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  decoration: BoxDecoration(
                    color: AppTheme.cardDark,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: _selectedStatus,
                      isExpanded: true,
                      dropdownColor: AppTheme.cardDark,
                      items: const [
                        DropdownMenuItem(value: 'all', child: Text('كل الحالات')),
                        DropdownMenuItem(value: 'active', child: Text('نشط')),
                        DropdownMenuItem(value: 'inactive', child: Text('غير نشط')),
                      ],
                      onChanged: (value) {
                        setState(() {
                          _selectedStatus = value ?? 'all';
                          _applyFilters();
                        });
                      },
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.restaurant_outlined, size: 80, color: Colors.white.withOpacity(0.3)),
          const SizedBox(height: 16),
          Text(
            _searchQuery.isNotEmpty ? 'لا توجد نتائج' : 'لا توجد مطاعم',
            style: TextStyle(fontSize: 18, color: Colors.white.withOpacity(0.6)),
          ),
          const SizedBox(height: 8),
          Text(
            _searchQuery.isNotEmpty
                ? 'جرب تغيير معايير البحث'
                : 'أضف أول مطعم للبدء',
            style: TextStyle(color: Colors.white.withOpacity(0.4)),
          ),
        ],
      ),
    );
  }

  Widget _buildRestaurantCard(Map<String, dynamic> restaurant) {
    final isActive = restaurant['is_active'] == true;
    final logoUrl = restaurant['logo_url'] as String?;
    final categoryName = _getCategoryName(restaurant['category_id']);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isActive
              ? Colors.transparent
              : AppTheme.errorColor.withOpacity(0.3),
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () async {
            final result = await Navigator.pushNamed(
              context,
              AppRoutes.restaurantDetails,
              arguments: {'restaurantId': restaurant['id']},
            );
            if (result == true) _loadData();
          },
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                // Logo
                Container(
                  width: 70,
                  height: 70,
                  decoration: BoxDecoration(
                    color: AppTheme.primaryColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: logoUrl != null && logoUrl.isNotEmpty
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(14),
                          child: CachedNetworkImage(
                            imageUrl: logoUrl,
                            fit: BoxFit.cover,
                            placeholder: (_, __) => const Center(
                              child: CircularProgressIndicator(strokeWidth: 2),
                            ),
                            errorWidget: (_, __, ___) => const Icon(
                              Icons.restaurant,
                              color: AppTheme.primaryColor,
                              size: 32,
                            ),
                          ),
                        )
                      : const Icon(
                          Icons.restaurant,
                          color: AppTheme.primaryColor,
                          size: 32,
                        ),
                ),
                const SizedBox(width: 16),

                // Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              restaurant['name_ar'] ?? restaurant['name'] ?? '',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          _buildStatusBadge(isActive),
                        ],
                      ),
                      const SizedBox(height: 4),
                      if (categoryName != null)
                        Text(
                          categoryName,
                          style: TextStyle(
                            color: AppTheme.primaryColor.withOpacity(0.8),
                            fontSize: 13,
                          ),
                        ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(
                            Icons.phone,
                            size: 14,
                            color: Colors.white.withOpacity(0.5),
                          ),
                          const SizedBox(width: 4),
                          Text(
                            restaurant['phone_number'] ?? '-',
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.6),
                              fontSize: 13,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: AppTheme.primaryColor.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              restaurant['subscription_tier'] ?? 'basic',
                              style: const TextStyle(
                                color: AppTheme.primaryColor,
                                fontSize: 11,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                // Actions menu
                PopupMenuButton<String>(
                  icon: Icon(
                    Icons.more_vert,
                    color: Colors.white.withOpacity(0.6),
                  ),
                  color: AppTheme.surfaceDark,
                  onSelected: (value) {
                    switch (value) {
                      case 'edit':
                        Navigator.pushNamed(
                          context,
                          AppRoutes.restaurantForm,
                          arguments: {'restaurant': restaurant},
                        ).then((result) {
                          if (result == true) _loadData();
                        });
                        break;
                      case 'toggle':
                        _toggleRestaurantStatus(restaurant);
                        break;
                      case 'delete':
                        _deleteRestaurant(restaurant);
                        break;
                    }
                  },
                  itemBuilder: (context) => [
                    const PopupMenuItem(
                      value: 'edit',
                      child: Row(
                        children: [
                          Icon(Icons.edit, size: 20),
                          SizedBox(width: 12),
                          Text('تعديل'),
                        ],
                      ),
                    ),
                    PopupMenuItem(
                      value: 'toggle',
                      child: Row(
                        children: [
                          Icon(
                            isActive ? Icons.block : Icons.check_circle,
                            size: 20,
                          ),
                          const SizedBox(width: 12),
                          Text(isActive ? 'تعطيل' : 'تفعيل'),
                        ],
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'delete',
                      child: Row(
                        children: [
                          Icon(Icons.delete, size: 20, color: AppTheme.errorColor),
                          SizedBox(width: 12),
                          Text('حذف', style: TextStyle(color: AppTheme.errorColor)),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatusBadge(bool isActive) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: (isActive ? AppTheme.accentColor : AppTheme.errorColor).withOpacity(0.15),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        isActive ? 'نشط' : 'معطل',
        style: TextStyle(
          color: isActive ? AppTheme.accentColor : AppTheme.errorColor,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  String? _getCategoryName(dynamic categoryId) {
    if (categoryId == null) return null;
    final category = _categories.firstWhere(
      (c) => c['id'] == categoryId,
      orElse: () => null,
    );
    if (category == null) return null;
    return category['name_ar'] ?? category['name'];
  }
}
