import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/services/api_service.dart';
import '../../../core/services/storage_service.dart';

class MenuManagementController extends GetxController {
  final ApiService _api = Get.find<ApiService>();
  final StorageService _storage = Get.find<StorageService>();

  final isLoading = true.obs;
  final menus = <Map<String, dynamic>>[].obs;
  final categories = <Map<String, dynamic>>[].obs;
  final menuItems = <Map<String, dynamic>>[].obs;
  
  final selectedMenuId = Rxn<int>();
  final selectedCategoryId = Rxn<int>();
  
  int? restaurantId;

  @override
  void onInit() {
    super.onInit();
    loadMenus();
  }

  Future<void> loadMenus() async {
    isLoading.value = true;
    try {
      restaurantId = await _storage.getRestaurantId();
      if (restaurantId != null) {
        final response = await _api.getMenus(restaurantId!);
        if (response.statusCode == 200) {
          menus.value = List<Map<String, dynamic>>.from(response.data);
          if (menus.isNotEmpty && selectedMenuId.value == null) {
            selectedMenuId.value = menus.first['id'];
            await loadCategories(selectedMenuId.value!);
          }
        }
      }
    } catch (e) {
      print('Error loading menus: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> loadCategories(int menuId) async {
    try {
      selectedMenuId.value = menuId;
      final response = await _api.getCategories(menuId);
      if (response.statusCode == 200) {
        categories.value = List<Map<String, dynamic>>.from(response.data);
      }
    } catch (e) {
      print('Error loading categories: $e');
    }
  }

  Future<void> loadMenuItems(int categoryId) async {
    try {
      selectedCategoryId.value = categoryId;
      final response = await _api.getMenuItems(categoryId);
      if (response.statusCode == 200) {
        menuItems.value = List<Map<String, dynamic>>.from(response.data);
      }
    } catch (e) {
      print('Error loading menu items: $e');
    }
  }

  // CRUD Operations for Menus
  Future<void> createMenu(String name) async {
    try {
      final response = await _api.createMenu({
        'name': name,
        'restaurant_id': restaurantId,
        'is_active': true,
      });
      if (response.statusCode == 200 || response.statusCode == 201) {
        Get.snackbar('نجاح', 'تم إنشاء القائمة');
        await loadMenus();
      }
    } catch (e) {
      Get.snackbar('خطأ', 'فشل إنشاء القائمة');
    }
  }

  Future<void> updateMenu(int id, String name) async {
    try {
      final response = await _api.updateMenu(id, {'name': name});
      if (response.statusCode == 200) {
        Get.snackbar('نجاح', 'تم تحديث القائمة');
        await loadMenus();
      }
    } catch (e) {
      Get.snackbar('خطأ', 'فشل تحديث القائمة');
    }
  }

  Future<void> deleteMenu(int id) async {
    try {
      final response = await _api.deleteMenu(id);
      if (response.statusCode == 200) {
        Get.snackbar('نجاح', 'تم حذف القائمة');
        selectedMenuId.value = null;
        await loadMenus();
      }
    } catch (e) {
      Get.snackbar('خطأ', 'فشل حذف القائمة');
    }
  }

  // CRUD Operations for Categories
  Future<void> createCategory(String name) async {
    if (selectedMenuId.value == null) return;
    try {
      final response = await _api.createCategory({
        'name': name,
        'menu_id': selectedMenuId.value,
      });
      if (response.statusCode == 200 || response.statusCode == 201) {
        Get.snackbar('نجاح', 'تم إنشاء الفئة');
        await loadCategories(selectedMenuId.value!);
      }
    } catch (e) {
      Get.snackbar('خطأ', 'فشل إنشاء الفئة');
    }
  }

  Future<void> updateCategory(int id, String name) async {
    try {
      final response = await _api.updateCategory(id, {'name': name});
      if (response.statusCode == 200) {
        Get.snackbar('نجاح', 'تم تحديث الفئة');
        if (selectedMenuId.value != null) {
          await loadCategories(selectedMenuId.value!);
        }
      }
    } catch (e) {
      Get.snackbar('خطأ', 'فشل تحديث الفئة');
    }
  }

  Future<void> deleteCategory(int id) async {
    try {
      final response = await _api.deleteCategory(id);
      if (response.statusCode == 200) {
        Get.snackbar('نجاح', 'تم حذف الفئة');
        if (selectedMenuId.value != null) {
          await loadCategories(selectedMenuId.value!);
        }
      }
    } catch (e) {
      Get.snackbar('خطأ', 'فشل حذف الفئة');
    }
  }

  // CRUD Operations for Menu Items
  Future<void> createMenuItem({
    required String name,
    required double price,
    String? description,
    String? imageUrl,
  }) async {
    if (selectedCategoryId.value == null) return;
    try {
      final response = await _api.createMenuItem({
        'name': name,
        'price': price,
        'description': description,
        'image_url': imageUrl,
        'category_id': selectedCategoryId.value,
        'is_available': true,
      });
      if (response.statusCode == 200 || response.statusCode == 201) {
        Get.snackbar('نجاح', 'تم إنشاء الصنف');
        await loadMenuItems(selectedCategoryId.value!);
      }
    } catch (e) {
      Get.snackbar('خطأ', 'فشل إنشاء الصنف');
    }
  }

  Future<void> updateMenuItem(int id, Map<String, dynamic> data) async {
    try {
      final response = await _api.updateMenuItem(id, data);
      if (response.statusCode == 200) {
        Get.snackbar('نجاح', 'تم تحديث الصنف');
        if (selectedCategoryId.value != null) {
          await loadMenuItems(selectedCategoryId.value!);
        }
      }
    } catch (e) {
      Get.snackbar('خطأ', 'فشل تحديث الصنف');
    }
  }

  Future<void> deleteMenuItem(int id) async {
    try {
      final response = await _api.deleteMenuItem(id);
      if (response.statusCode == 200) {
        Get.snackbar('نجاح', 'تم حذف الصنف');
        if (selectedCategoryId.value != null) {
          await loadMenuItems(selectedCategoryId.value!);
        }
      }
    } catch (e) {
      Get.snackbar('خطأ', 'فشل حذف الصنف');
    }
  }

  Future<void> toggleItemAvailability(int id, bool isAvailable) async {
    await updateMenuItem(id, {'is_available': isAvailable});
  }
}
