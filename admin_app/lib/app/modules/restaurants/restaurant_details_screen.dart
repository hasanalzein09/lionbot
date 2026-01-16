import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';
import '../../routes/app_routes.dart';

class RestaurantDetailsScreen extends StatefulWidget {
  final int? restaurantId;

  const RestaurantDetailsScreen({super.key, this.restaurantId});

  @override
  State<RestaurantDetailsScreen> createState() => _RestaurantDetailsScreenState();
}

class _RestaurantDetailsScreenState extends State<RestaurantDetailsScreen> {
  Map<String, dynamic>? _restaurant;
  List<dynamic> _menus = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    if (widget.restaurantId == null) return;

    setState(() => _isLoading = true);
    try {
      final results = await Future.wait([
        ApiService().getRestaurant(widget.restaurantId!),
        ApiService().getMenus(widget.restaurantId!),
      ]);

      if (mounted) {
        setState(() {
          _restaurant = results[0] as Map<String, dynamic>;
          _menus = results[1] as List<dynamic>;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        _showError('فشل تحميل بيانات المطعم');
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppTheme.errorColor),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppTheme.accentColor),
    );
  }

  Future<void> _deleteRestaurant() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardDark,
        title: const Text('حذف المطعم'),
        content: const Text('هل أنت متأكد من حذف هذا المطعم؟ سيتم حذف جميع القوائم والأصناف.'),
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
        await ApiService().deleteRestaurant(widget.restaurantId!);
        _showSuccess('تم حذف المطعم بنجاح');
        if (mounted) Navigator.pop(context, true);
      } catch (e) {
        _showError('فشل حذف المطعم');
      }
    }
  }

  Future<void> _showAddCategoryDialog({int? menuId, Map<String, dynamic>? category}) async {
    final nameController = TextEditingController(text: category?['name'] ?? '');
    final nameArController = TextEditingController(text: category?['name_ar'] ?? '');
    final isEditing = category != null;

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardDark,
        title: Text(isEditing ? 'تعديل الفئة' : 'إضافة فئة'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                labelText: 'اسم الفئة (إنجليزي)',
                hintText: 'Category Name',
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: nameArController,
              decoration: const InputDecoration(
                labelText: 'اسم الفئة (عربي)',
                hintText: 'اسم الفئة',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (nameController.text.trim().isEmpty) return;

              try {
                int? targetMenuId = menuId;

                // If no menu exists, create one first
                if (targetMenuId == null && !isEditing) {
                  final newMenu = await ApiService().createMenu({
                    'restaurant_id': widget.restaurantId,
                    'name': 'Main Menu',
                    'name_ar': 'القائمة الرئيسية',
                    'is_active': true,
                  });
                  targetMenuId = newMenu['id'];
                }

                final data = {
                  'name': nameController.text.trim(),
                  'name_ar': nameArController.text.trim().isEmpty ? null : nameArController.text.trim(),
                  if (!isEditing && targetMenuId != null) 'menu_id': targetMenuId,
                };

                if (isEditing) {
                  await ApiService().updateMenuCategory(category['id'], data);
                } else {
                  await ApiService().createMenuCategory(data);
                }

                Navigator.pop(ctx, true);
              } catch (e) {
                if (ctx.mounted) {
                  ScaffoldMessenger.of(ctx).showSnackBar(
                    SnackBar(content: Text('فشل: $e'), backgroundColor: AppTheme.errorColor),
                  );
                }
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryColor),
            child: Text(isEditing ? 'حفظ' : 'إضافة'),
          ),
        ],
      ),
    );

    if (result == true) {
      _loadData();
    }
  }

  Future<void> _deleteCategory(int categoryId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardDark,
        title: const Text('حذف الفئة'),
        content: const Text('هل أنت متأكد؟ سيتم حذف جميع الأصناف في هذه الفئة.'),
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
        await ApiService().deleteMenuCategory(categoryId);
        _showSuccess('تم حذف الفئة');
        _loadData();
      } catch (e) {
        _showError('فشل حذف الفئة');
      }
    }
  }

  Future<void> _deleteMenuItem(int itemId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardDark,
        title: const Text('حذف الصنف'),
        content: const Text('هل أنت متأكد من حذف هذا الصنف؟'),
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
        await ApiService().deleteMenuItem(itemId);
        _showSuccess('تم حذف الصنف');
        _loadData();
      } catch (e) {
        _showError('فشل حذف الصنف');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('تفاصيل المطعم')),
        body: const Center(child: CircularProgressIndicator(color: AppTheme.primaryColor)),
      );
    }

    if (_restaurant == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('تفاصيل المطعم')),
        body: const Center(child: Text('المطعم غير موجود')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(_restaurant!['name_ar'] ?? _restaurant!['name'] ?? 'المطعم'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () async {
              final result = await Navigator.pushNamed(
                context,
                AppRoutes.restaurantForm,
                arguments: {'restaurant': _restaurant},
              );
              if (result == true) _loadData();
            },
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert),
            color: AppTheme.surfaceDark,
            onSelected: (value) {
              if (value == 'delete') _deleteRestaurant();
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'delete',
                child: Row(
                  children: [
                    Icon(Icons.delete, color: AppTheme.errorColor),
                    SizedBox(width: 12),
                    Text('حذف المطعم', style: TextStyle(color: AppTheme.errorColor)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddCategoryDialog(menuId: _menus.isNotEmpty ? _menus.first['id'] : null),
        backgroundColor: AppTheme.primaryColor,
        icon: const Icon(Icons.add),
        label: const Text('إضافة فئة'),
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(),
              _buildStats(),
              _buildMenuSection(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    final isActive = _restaurant!['is_active'] == true;
    final logoUrl = _restaurant!['logo_url'] as String?;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        border: Border(bottom: BorderSide(color: Colors.white.withAlpha(25))),
      ),
      child: Row(
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: AppTheme.primaryColor.withAlpha(25),
              borderRadius: BorderRadius.circular(16),
            ),
            child: logoUrl != null && logoUrl.isNotEmpty
                ? ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Image.network(
                      logoUrl,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => const Icon(
                        Icons.restaurant,
                        color: AppTheme.primaryColor,
                        size: 40,
                      ),
                    ),
                  )
                : const Icon(Icons.restaurant, color: AppTheme.primaryColor, size: 40),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        _restaurant!['name_ar'] ?? _restaurant!['name'] ?? '',
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: (isActive ? AppTheme.accentColor : AppTheme.errorColor).withAlpha(38),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        isActive ? 'نشط' : 'معطل',
                        style: TextStyle(
                          color: isActive ? AppTheme.accentColor : AppTheme.errorColor,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                if (_restaurant!['phone_number'] != null)
                  Row(
                    children: [
                      Icon(Icons.phone, size: 16, color: Colors.white.withAlpha(150)),
                      const SizedBox(width: 6),
                      Text(_restaurant!['phone_number'], style: TextStyle(color: Colors.white.withAlpha(180))),
                    ],
                  ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryColor.withAlpha(25),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        _restaurant!['subscription_tier'] ?? 'basic',
                        style: const TextStyle(color: AppTheme.primaryColor, fontSize: 12),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'العمولة: ${((_restaurant!['commission_rate'] ?? 0) * 100).toStringAsFixed(0)}%',
                      style: TextStyle(color: Colors.white.withAlpha(150), fontSize: 12),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStats() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          _buildStatCard('الطلبات', '0', Icons.shopping_bag),
          const SizedBox(width: 12),
          _buildStatCard('الإيرادات', '\$0', Icons.attach_money),
          const SizedBox(width: 12),
          _buildStatCard('الأصناف', _countItems().toString(), Icons.restaurant_menu),
        ],
      ),
    );
  }

  int _countItems() {
    int count = 0;
    for (final menu in _menus) {
      final categories = menu['categories'] as List? ?? [];
      for (final cat in categories) {
        count += (cat['items'] as List? ?? []).length;
      }
    }
    return count;
  }

  Widget _buildStatCard(String label, String value, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.cardDark,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Icon(icon, color: AppTheme.primaryColor, size: 28),
            const SizedBox(height: 8),
            Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(label, style: TextStyle(fontSize: 12, color: Colors.white.withAlpha(150))),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuSection() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text('القائمة', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const Spacer(),
              Text('${_countItems()} صنف', style: TextStyle(color: Colors.white.withAlpha(150))),
            ],
          ),
          const SizedBox(height: 16),
          if (_menus.isEmpty)
            _buildEmptyMenu()
          else
            ..._menus.map((menu) => _buildMenuCategories(menu)),
        ],
      ),
    );
  }

  Widget _buildEmptyMenu() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(40),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withAlpha(25)),
      ),
      child: Column(
        children: [
          Icon(Icons.restaurant_menu, size: 60, color: Colors.white.withAlpha(75)),
          const SizedBox(height: 16),
          Text('لا توجد أصناف', style: TextStyle(fontSize: 18, color: Colors.white.withAlpha(180))),
          const SizedBox(height: 8),
          Text('أضف فئات وأصناف للقائمة', style: TextStyle(color: Colors.white.withAlpha(100))),
        ],
      ),
    );
  }

  Widget _buildMenuCategories(Map<String, dynamic> menu) {
    final categories = menu['categories'] as List? ?? [];

    if (categories.isEmpty) return _buildEmptyMenu();

    return Column(
      children: categories.map<Widget>((category) {
        final items = category['items'] as List? ?? [];

        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          decoration: BoxDecoration(
            color: AppTheme.cardDark,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Theme(
            data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
            child: ExpansionTile(
              initiallyExpanded: true,
              tilePadding: const EdgeInsets.symmetric(horizontal: 16),
              title: Row(
                children: [
                  Expanded(
                    child: Text(
                      category['name_ar'] ?? category['name'] ?? '',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                  ),
                  Text('${items.length} صنف', style: TextStyle(fontSize: 13, color: Colors.white.withAlpha(150))),
                ],
              ),
              trailing: PopupMenuButton<String>(
                icon: Icon(Icons.more_vert, color: Colors.white.withAlpha(150)),
                color: AppTheme.surfaceDark,
                onSelected: (value) {
                  switch (value) {
                    case 'edit':
                      _showAddCategoryDialog(menuId: menu['id'], category: category);
                      break;
                    case 'add_item':
                      Navigator.pushNamed(context, AppRoutes.menuItemForm, arguments: {
                        'restaurantId': widget.restaurantId,
                        'categoryId': category['id'],
                      }).then((result) {
                        if (result == true) _loadData();
                      });
                      break;
                    case 'delete':
                      _deleteCategory(category['id']);
                      break;
                  }
                },
                itemBuilder: (context) => [
                  const PopupMenuItem(value: 'add_item', child: Row(children: [Icon(Icons.add, size: 20), SizedBox(width: 12), Text('إضافة صنف')])),
                  const PopupMenuItem(value: 'edit', child: Row(children: [Icon(Icons.edit, size: 20), SizedBox(width: 12), Text('تعديل')])),
                  const PopupMenuItem(value: 'delete', child: Row(children: [Icon(Icons.delete, size: 20, color: AppTheme.errorColor), SizedBox(width: 12), Text('حذف', style: TextStyle(color: AppTheme.errorColor))])),
                ],
              ),
              children: [
                if (items.isEmpty)
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text('لا توجد أصناف في هذه الفئة', style: TextStyle(color: Colors.white.withAlpha(100))),
                  )
                else
                  ...items.map<Widget>((item) => _buildMenuItem(item, category['id'])),
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: OutlinedButton.icon(
                    onPressed: () {
                      Navigator.pushNamed(context, AppRoutes.menuItemForm, arguments: {
                        'restaurantId': widget.restaurantId,
                        'categoryId': category['id'],
                      }).then((result) {
                        if (result == true) _loadData();
                      });
                    },
                    icon: const Icon(Icons.add, size: 18),
                    label: const Text('إضافة صنف'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppTheme.primaryColor,
                      side: BorderSide(color: AppTheme.primaryColor.withAlpha(100)),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildMenuItem(Map<String, dynamic> item, int categoryId) {
    final isAvailable = item['is_available'] == true;
    final hasVariants = item['has_variants'] == true;
    final price = item['price'] ?? 0;
    final priceMin = item['price_min'];
    final priceMax = item['price_max'];

    String priceText;
    if (hasVariants && priceMin != null && priceMax != null) {
      priceText = '\$$priceMin - \$$priceMax';
    } else {
      priceText = '\$$price';
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isAvailable ? Colors.transparent : AppTheme.errorColor.withAlpha(75)),
      ),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: AppTheme.primaryColor.withAlpha(25),
              borderRadius: BorderRadius.circular(10),
            ),
            child: item['image_url'] != null
                ? ClipRRect(
                    borderRadius: BorderRadius.circular(10),
                    child: Image.network(
                      item['image_url'],
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => const Icon(Icons.fastfood, color: AppTheme.primaryColor),
                    ),
                  )
                : const Icon(Icons.fastfood, color: AppTheme.primaryColor),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        item['name_ar'] ?? item['name'] ?? '',
                        style: const TextStyle(fontWeight: FontWeight.w500),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    if (!isAvailable)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppTheme.errorColor.withAlpha(38),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text('غير متوفر', style: TextStyle(color: AppTheme.errorColor, fontSize: 10)),
                      ),
                  ],
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Text(priceText, style: const TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold)),
                    if (hasVariants) ...[
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(color: Colors.blue.withAlpha(38), borderRadius: BorderRadius.circular(8)),
                        child: const Text('أحجام', style: TextStyle(color: Colors.blue, fontSize: 10)),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
          PopupMenuButton<String>(
            icon: Icon(Icons.more_vert, size: 20, color: Colors.white.withAlpha(150)),
            color: AppTheme.surfaceDark,
            onSelected: (value) {
              switch (value) {
                case 'edit':
                  Navigator.pushNamed(context, AppRoutes.menuItemForm, arguments: {
                    'restaurantId': widget.restaurantId,
                    'categoryId': categoryId,
                    'menuItem': item,
                  }).then((result) {
                    if (result == true) _loadData();
                  });
                  break;
                case 'delete':
                  _deleteMenuItem(item['id']);
                  break;
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'edit', child: Row(children: [Icon(Icons.edit, size: 18), SizedBox(width: 10), Text('تعديل')])),
              const PopupMenuItem(value: 'delete', child: Row(children: [Icon(Icons.delete, size: 18, color: AppTheme.errorColor), SizedBox(width: 10), Text('حذف', style: TextStyle(color: AppTheme.errorColor))])),
            ],
          ),
        ],
      ),
    );
  }
}
