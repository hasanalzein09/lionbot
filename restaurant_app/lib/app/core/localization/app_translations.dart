import 'package:get/get.dart';

class AppTranslations extends Translations {
  @override
  Map<String, Map<String, String>> get keys => {
    'en_US': {
      // Auth
      'login': 'Login',
      'logout': 'Logout',
      'sign_in': 'Sign In',
      'restaurant_login': 'Restaurant Login',
      'manage_orders': 'Sign in to manage your orders',
      'login_failed': 'Login failed. Please check your credentials.',
      
      // Navigation
      'dashboard': 'Dashboard',
      'orders': 'Orders',
      'menu': 'Menu',
      'settings': 'Settings',
      
      // Dashboard
      'new_orders': 'New Orders',
      'preparing': 'Preparing',
      'ready': 'Ready',
      'today_revenue': "Today's Revenue",
      'view_orders': 'View Orders',
      'edit_menu': 'Edit Menu',
      
      // Orders
      'all_orders': 'All',
      'new': 'New',
      'order_details': 'Order Details',
      'accept': 'Accept',
      'mark_ready': 'Mark Ready',
      'picked_up': 'Picked Up',
      'no_orders': 'No orders',
      
      // Status
      'pending': 'Pending',
      'accepted': 'Accepted',
      'out_for_delivery': 'Out for Delivery',
      'delivered': 'Delivered',
      'cancelled': 'Cancelled',
      
      // Menu
      'menu_management': 'Menu Management',
      'add_item': 'Add Item',
      'edit_item': 'Edit Item',
      'category': 'Category',
      'price': 'Price',
      'available': 'Available',
      'unavailable': 'Unavailable',
      
      // Settings
      'working_hours': 'Working Hours',
      'delivery_settings': 'Delivery Settings',
      'notifications': 'Notifications',
      'printer_setup': 'Printer Setup',
      
      // Common
      'loading': 'Loading...',
      'refresh': 'Refresh',
      'save': 'Save',
      'cancel': 'Cancel',
      'confirm': 'Confirm',
      
      // Payment
      'cash_on_delivery': 'Cash on Delivery',
      'total': 'Total',
      'items': 'Items',
    },
    
    'ar_SA': {
      // Auth
      'login': 'تسجيل الدخول',
      'logout': 'تسجيل الخروج',
      'sign_in': 'دخول',
      'restaurant_login': 'دخول المطعم',
      'manage_orders': 'سجل دخولك لإدارة طلباتك',
      'login_failed': 'فشل تسجيل الدخول. تحقق من بياناتك.',
      
      // Navigation
      'dashboard': 'لوحة التحكم',
      'orders': 'الطلبات',
      'menu': 'القائمة',
      'settings': 'الإعدادات',
      
      // Dashboard
      'new_orders': 'طلبات جديدة',
      'preparing': 'قيد التحضير',
      'ready': 'جاهز',
      'today_revenue': 'إيرادات اليوم',
      'view_orders': 'عرض الطلبات',
      'edit_menu': 'تعديل القائمة',
      
      // Orders
      'all_orders': 'الكل',
      'new': 'جديد',
      'order_details': 'تفاصيل الطلب',
      'accept': 'قبول',
      'mark_ready': 'تحديد جاهز',
      'picked_up': 'تم الاستلام',
      'no_orders': 'لا توجد طلبات',
      
      // Status
      'pending': 'قيد الانتظار',
      'accepted': 'مقبول',
      'out_for_delivery': 'في الطريق',
      'delivered': 'تم التوصيل',
      'cancelled': 'ملغي',
      
      // Menu
      'menu_management': 'إدارة القائمة',
      'add_item': 'إضافة عنصر',
      'edit_item': 'تعديل عنصر',
      'category': 'الفئة',
      'price': 'السعر',
      'available': 'متوفر',
      'unavailable': 'غير متوفر',
      
      // Settings
      'working_hours': 'ساعات العمل',
      'delivery_settings': 'إعدادات التوصيل',
      'notifications': 'الإشعارات',
      'printer_setup': 'إعداد الطابعة',
      
      // Common
      'loading': 'جاري التحميل...',
      'refresh': 'تحديث',
      'save': 'حفظ',
      'cancel': 'إلغاء',
      'confirm': 'تأكيد',
      
      // Payment
      'cash_on_delivery': 'الدفع عند الاستلام',
      'total': 'الإجمالي',
      'items': 'عناصر',
    },
  };
}
