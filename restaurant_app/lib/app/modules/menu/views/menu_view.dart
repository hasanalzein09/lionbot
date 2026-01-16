import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../controllers/menu_controller.dart';

class MenuView extends GetView<MenuManagementController> {
  const MenuView({super.key});

  @override
  Widget build(BuildContext context) {
    // Register controller if not exists
    if (!Get.isRegistered<MenuManagementController>()) {
      Get.put(MenuManagementController());
    }
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('إدارة القائمة'),
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: controller.loadMenus,
          ),
        ],
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }

        return Column(
          children: [
            // Menu Selector
            Container(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: Obx(() => DropdownButtonFormField<int>(
                      value: controller.selectedMenuId.value,
                      decoration: const InputDecoration(
                        labelText: 'اختر القائمة',
                        border: OutlineInputBorder(),
                      ),
                      items: controller.menus.map((menu) {
                        return DropdownMenuItem<int>(
                          value: menu['id'],
                          child: Text(menu['name']),
                        );
                      }).toList(),
                      onChanged: (value) {
                        if (value != null) {
                          controller.loadCategories(value);
                        }
                      },
                    )),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.add),
                    onPressed: () => _showAddMenuDialog(context),
                  ),
                  IconButton(
                    icon: const Icon(Icons.edit),
                    onPressed: controller.selectedMenuId.value != null
                        ? () => _showEditMenuDialog(context)
                        : null,
                  ),
                ],
              ),
            ),
            
            const Divider(),
            
            // Categories and Items
            Expanded(
              child: Obx(() {
                if (controller.categories.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.category, size: 64, color: Colors.grey[300]),
                        const SizedBox(height: 16),
                        const Text('لا توجد فئات'),
                        const SizedBox(height: 16),
                        ElevatedButton.icon(
                          onPressed: () => _showAddCategoryDialog(context),
                          icon: const Icon(Icons.add),
                          label: const Text('إضافة فئة'),
                        ),
                      ],
                    ),
                  );
                }

                return ListView.builder(
                  itemCount: controller.categories.length,
                  itemBuilder: (context, index) {
                    final category = controller.categories[index];
                    return _buildCategorySection(context, category);
                  },
                );
              }),
            ),
          ],
        );
      }),
      floatingActionButton: Obx(() => controller.selectedMenuId.value != null
          ? FloatingActionButton(
              onPressed: () => _showAddCategoryDialog(context),
              child: const Icon(Icons.add),
            )
          : const SizedBox.shrink()),
    );
  }

  Widget _buildCategorySection(BuildContext context, Map<String, dynamic> category) {
    return ExpansionTile(
      title: Text(
        category['name'],
        style: const TextStyle(fontWeight: FontWeight.bold),
      ),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            icon: const Icon(Icons.add, size: 20),
            onPressed: () {
              controller.selectedCategoryId.value = category['id'];
              _showAddItemDialog(context);
            },
          ),
          IconButton(
            icon: const Icon(Icons.edit, size: 20),
            onPressed: () => _showEditCategoryDialog(context, category),
          ),
          IconButton(
            icon: const Icon(Icons.delete, size: 20, color: Colors.red),
            onPressed: () => _showDeleteCategoryDialog(context, category['id']),
          ),
        ],
      ),
      onExpansionChanged: (expanded) {
        if (expanded) {
          controller.loadMenuItems(category['id']);
        }
      },
      children: [
        Obx(() {
          final items = controller.menuItems
              .where((item) => item['category_id'] == category['id'])
              .toList();
          
          if (items.isEmpty) {
            return const ListTile(
              title: Text('لا توجد أصناف', style: TextStyle(color: Colors.grey)),
            );
          }

          return Column(
            children: items.map((item) => _buildMenuItem(context, item)).toList(),
          );
        }),
      ],
    );
  }

  Widget _buildMenuItem(BuildContext context, Map<String, dynamic> item) {
    return ListTile(
      leading: item['image_url'] != null
          ? ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                item['image_url'],
                width: 50,
                height: 50,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => Container(
                  width: 50,
                  height: 50,
                  color: Colors.grey[200],
                  child: const Icon(Icons.restaurant),
                ),
              ),
            )
          : Container(
              width: 50,
              height: 50,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.restaurant),
            ),
      title: Text(item['name']),
      subtitle: Text(
        '\$${item['price']?.toStringAsFixed(2) ?? '0.00'}',
        style: TextStyle(color: Theme.of(context).colorScheme.primary),
      ),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Switch(
            value: item['is_available'] ?? true,
            onChanged: (value) {
              controller.toggleItemAvailability(item['id'], value);
            },
          ),
          IconButton(
            icon: const Icon(Icons.edit, size: 20),
            onPressed: () => _showEditItemDialog(context, item),
          ),
          IconButton(
            icon: const Icon(Icons.delete, size: 20, color: Colors.red),
            onPressed: () => _showDeleteItemDialog(context, item['id']),
          ),
        ],
      ),
    );
  }

  // Dialog Methods
  void _showAddMenuDialog(BuildContext context) {
    final controller = TextEditingController();
    Get.dialog(
      AlertDialog(
        title: const Text('إضافة قائمة جديدة'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'اسم القائمة',
            hintText: 'مثال: قائمة الغداء',
          ),
        ),
        actions: [
          TextButton(onPressed: () => Get.back(), child: const Text('إلغاء')),
          ElevatedButton(
            onPressed: () {
              if (controller.text.isNotEmpty) {
                this.controller.createMenu(controller.text);
                Get.back();
              }
            },
            child: const Text('إضافة'),
          ),
        ],
      ),
    );
  }

  void _showEditMenuDialog(BuildContext context) {
    final menu = controller.menus.firstWhere(
      (m) => m['id'] == controller.selectedMenuId.value,
    );
    final textController = TextEditingController(text: menu['name']);
    
    Get.dialog(
      AlertDialog(
        title: const Text('تعديل القائمة'),
        content: TextField(
          controller: textController,
          decoration: const InputDecoration(labelText: 'اسم القائمة'),
        ),
        actions: [
          TextButton(onPressed: () => Get.back(), child: const Text('إلغاء')),
          TextButton(
            onPressed: () {
              _showDeleteMenuDialog(context, menu['id']);
            },
            child: const Text('حذف', style: TextStyle(color: Colors.red)),
          ),
          ElevatedButton(
            onPressed: () {
              if (textController.text.isNotEmpty) {
                controller.updateMenu(menu['id'], textController.text);
                Get.back();
              }
            },
            child: const Text('حفظ'),
          ),
        ],
      ),
    );
  }

  void _showDeleteMenuDialog(BuildContext context, int id) {
    Get.dialog(
      AlertDialog(
        title: const Text('حذف القائمة'),
        content: const Text('هل أنت متأكد؟ سيتم حذف جميع الفئات والأصناف.'),
        actions: [
          TextButton(onPressed: () => Get.back(), child: const Text('إلغاء')),
          ElevatedButton(
            onPressed: () {
              controller.deleteMenu(id);
              Get.back();
              Get.back();
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('حذف'),
          ),
        ],
      ),
    );
  }

  void _showAddCategoryDialog(BuildContext context) {
    final textController = TextEditingController();
    Get.dialog(
      AlertDialog(
        title: const Text('إضافة فئة جديدة'),
        content: TextField(
          controller: textController,
          decoration: const InputDecoration(
            labelText: 'اسم الفئة',
            hintText: 'مثال: المقبلات',
          ),
        ),
        actions: [
          TextButton(onPressed: () => Get.back(), child: const Text('إلغاء')),
          ElevatedButton(
            onPressed: () {
              if (textController.text.isNotEmpty) {
                controller.createCategory(textController.text);
                Get.back();
              }
            },
            child: const Text('إضافة'),
          ),
        ],
      ),
    );
  }

  void _showEditCategoryDialog(BuildContext context, Map<String, dynamic> category) {
    final textController = TextEditingController(text: category['name']);
    Get.dialog(
      AlertDialog(
        title: const Text('تعديل الفئة'),
        content: TextField(
          controller: textController,
          decoration: const InputDecoration(labelText: 'اسم الفئة'),
        ),
        actions: [
          TextButton(onPressed: () => Get.back(), child: const Text('إلغاء')),
          ElevatedButton(
            onPressed: () {
              if (textController.text.isNotEmpty) {
                controller.updateCategory(category['id'], textController.text);
                Get.back();
              }
            },
            child: const Text('حفظ'),
          ),
        ],
      ),
    );
  }

  void _showDeleteCategoryDialog(BuildContext context, int id) {
    Get.dialog(
      AlertDialog(
        title: const Text('حذف الفئة'),
        content: const Text('هل أنت متأكد؟ سيتم حذف جميع الأصناف.'),
        actions: [
          TextButton(onPressed: () => Get.back(), child: const Text('إلغاء')),
          ElevatedButton(
            onPressed: () {
              controller.deleteCategory(id);
              Get.back();
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('حذف'),
          ),
        ],
      ),
    );
  }

  void _showAddItemDialog(BuildContext context) {
    final nameController = TextEditingController();
    final priceController = TextEditingController();
    final descController = TextEditingController();
    
    Get.dialog(
      AlertDialog(
        title: const Text('إضافة صنف جديد'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(labelText: 'اسم الصنف'),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: priceController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'السعر'),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: descController,
                maxLines: 2,
                decoration: const InputDecoration(labelText: 'الوصف (اختياري)'),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Get.back(), child: const Text('إلغاء')),
          ElevatedButton(
            onPressed: () {
              if (nameController.text.isNotEmpty && priceController.text.isNotEmpty) {
                controller.createMenuItem(
                  name: nameController.text,
                  price: double.tryParse(priceController.text) ?? 0,
                  description: descController.text.isEmpty ? null : descController.text,
                );
                Get.back();
              }
            },
            child: const Text('إضافة'),
          ),
        ],
      ),
    );
  }

  void _showEditItemDialog(BuildContext context, Map<String, dynamic> item) {
    final nameController = TextEditingController(text: item['name']);
    final priceController = TextEditingController(text: item['price']?.toString() ?? '');
    final descController = TextEditingController(text: item['description'] ?? '');
    
    Get.dialog(
      AlertDialog(
        title: const Text('تعديل الصنف'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(labelText: 'اسم الصنف'),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: priceController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'السعر'),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: descController,
                maxLines: 2,
                decoration: const InputDecoration(labelText: 'الوصف'),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Get.back(), child: const Text('إلغاء')),
          ElevatedButton(
            onPressed: () {
              controller.updateMenuItem(item['id'], {
                'name': nameController.text,
                'price': double.tryParse(priceController.text) ?? 0,
                'description': descController.text,
              });
              Get.back();
            },
            child: const Text('حفظ'),
          ),
        ],
      ),
    );
  }

  void _showDeleteItemDialog(BuildContext context, int id) {
    Get.dialog(
      AlertDialog(
        title: const Text('حذف الصنف'),
        content: const Text('هل أنت متأكد من حذف هذا الصنف؟'),
        actions: [
          TextButton(onPressed: () => Get.back(), child: const Text('إلغاء')),
          ElevatedButton(
            onPressed: () {
              controller.deleteMenuItem(id);
              Get.back();
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('حذف'),
          ),
        ],
      ),
    );
  }
}
