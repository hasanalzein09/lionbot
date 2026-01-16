import 'package:get/get.dart';

class AppTranslations extends Translations {
  @override
  Map<String, Map<String, String>> get keys => {
    'en_US': {
      // Auth
      'login': 'Login',
      'logout': 'Logout',
      'email': 'Email',
      'password': 'Password',
      'sign_in': 'Sign In',
      'admin_login': 'Admin Login',
      'manage_platform': 'Sign in to manage your platform',
      'access_denied': 'Access denied. Admin privileges required.',
      'login_failed': 'Login failed. Please check your credentials.',
      
      // Navigation
      'dashboard': 'Dashboard',
      'orders': 'Orders',
      'restaurants': 'Restaurants',
      'drivers': 'Drivers',
      'inventory': 'Inventory',
      'loyalty': 'Loyalty',
      'settings': 'Settings',
      'analytics': 'Analytics',
      
      // Dashboard
      'today_revenue': "Today's Revenue",
      'pending_orders': 'Pending Orders',
      'active_drivers': 'Active Drivers',
      'total_orders': 'Total Orders',
      'quick_actions': 'Quick Actions',
      'recent_activity': 'Recent Activity',
      
      // Orders
      'all_orders': 'All Orders',
      'new_orders': 'New Orders',
      'preparing': 'Preparing',
      'ready': 'Ready',
      'delivery': 'Delivery',
      'delivered': 'Delivered',
      'cancelled': 'Cancelled',
      'order_details': 'Order Details',
      'update_status': 'Update Status',
      'assign_driver': 'Assign Driver',
      'auto_assign': 'Auto Assign',
      
      // Restaurants
      'add_restaurant': 'Add Restaurant',
      'edit_restaurant': 'Edit Restaurant',
      'active': 'Active',
      'inactive': 'Inactive',
      'branches': 'Branches',
      'menu_items': 'Menu Items',
      
      // Drivers
      'online_drivers': 'Online Drivers',
      'offline_drivers': 'Offline Drivers',
      'active_deliveries': 'Active Deliveries',
      'completed_today': 'Completed Today',
      'driver_details': 'Driver Details',
      'driver_stats': 'Driver Stats',
      
      // Inventory
      'low_stock': 'Low Stock',
      'out_of_stock': 'Out of Stock',
      'add_stock': 'Add Stock',
      'deduct_stock': 'Deduct Stock',
      'stock_value': 'Stock Value',
      'total_items': 'Total Items',
      
      // Loyalty
      'loyalty_program': 'Loyalty Program',
      'tiers': 'Tiers',
      'rewards': 'Rewards',
      'points': 'Points',
      'bronze': 'Bronze',
      'silver': 'Silver',
      'gold': 'Gold',
      'platinum': 'Platinum',
      
      // Settings
      'business_settings': 'Business Settings',
      'app_settings': 'App Settings',
      'delivery_fee': 'Delivery Fee',
      'min_order': 'Min Order',
      'max_radius': 'Max Radius',
      'notifications': 'Notifications',
      
      // Common
      'loading': 'Loading...',
      'refresh': 'Refresh',
      'save': 'Save',
      'cancel': 'Cancel',
      'delete': 'Delete',
      'edit': 'Edit',
      'add': 'Add',
      'search': 'Search',
      'filter': 'Filter',
      'no_data': 'No data available',
      'confirm': 'Confirm',
      'success': 'Success',
      'error': 'Error',
      
      // Payment
      'cash_on_delivery': 'Cash on Delivery',
      'payment_method': 'Payment Method',
      'total_amount': 'Total Amount',
    },
    
    'ar_SA': {
      // Auth
      'login': 'تسجيل الدخول',
      'logout': 'تسجيل الخروج',
      'email': 'البريد الإلكتروني',
      'password': 'كلمة المرور',
      'sign_in': 'دخول',
      'admin_login': 'دخول المسؤول',
      'manage_platform': 'سجل دخولك لإدارة المنصة',
      'access_denied': 'تم رفض الوصول. صلاحيات المسؤول مطلوبة.',
      'login_failed': 'فشل تسجيل الدخول. تحقق من بياناتك.',
      
      // Navigation
      'dashboard': 'لوحة التحكم',
      'orders': 'الطلبات',
      'restaurants': 'المطاعم',
      'drivers': 'السائقين',
      'inventory': 'المخزون',
      'loyalty': 'الولاء',
      'settings': 'الإعدادات',
      'analytics': 'التحليلات',
      
      // Dashboard
      'today_revenue': 'إيرادات اليوم',
      'pending_orders': 'الطلبات المعلقة',
      'active_drivers': 'السائقين النشطين',
      'total_orders': 'إجمالي الطلبات',
      'quick_actions': 'إجراءات سريعة',
      'recent_activity': 'النشاط الأخير',
      
      // Orders
      'all_orders': 'كل الطلبات',
      'new_orders': 'طلبات جديدة',
      'preparing': 'قيد التحضير',
      'ready': 'جاهز',
      'delivery': 'في التوصيل',
      'delivered': 'تم التوصيل',
      'cancelled': 'ملغي',
      'order_details': 'تفاصيل الطلب',
      'update_status': 'تحديث الحالة',
      'assign_driver': 'تعيين سائق',
      'auto_assign': 'تعيين تلقائي',
      
      // Restaurants
      'add_restaurant': 'إضافة مطعم',
      'edit_restaurant': 'تعديل المطعم',
      'active': 'نشط',
      'inactive': 'غير نشط',
      'branches': 'الفروع',
      'menu_items': 'عناصر القائمة',
      
      // Drivers
      'online_drivers': 'سائقين متصلين',
      'offline_drivers': 'سائقين غير متصلين',
      'active_deliveries': 'توصيلات نشطة',
      'completed_today': 'مكتمل اليوم',
      'driver_details': 'تفاصيل السائق',
      'driver_stats': 'إحصائيات السائق',
      
      // Inventory
      'low_stock': 'مخزون منخفض',
      'out_of_stock': 'نفذ من المخزون',
      'add_stock': 'إضافة مخزون',
      'deduct_stock': 'خصم مخزون',
      'stock_value': 'قيمة المخزون',
      'total_items': 'إجمالي العناصر',
      
      // Loyalty
      'loyalty_program': 'برنامج الولاء',
      'tiers': 'المستويات',
      'rewards': 'المكافآت',
      'points': 'نقاط',
      'bronze': 'برونزي',
      'silver': 'فضي',
      'gold': 'ذهبي',
      'platinum': 'بلاتيني',
      
      // Settings
      'business_settings': 'إعدادات العمل',
      'app_settings': 'إعدادات التطبيق',
      'delivery_fee': 'رسوم التوصيل',
      'min_order': 'الحد الأدنى للطلب',
      'max_radius': 'أقصى نطاق',
      'notifications': 'الإشعارات',
      
      // Common
      'loading': 'جاري التحميل...',
      'refresh': 'تحديث',
      'save': 'حفظ',
      'cancel': 'إلغاء',
      'delete': 'حذف',
      'edit': 'تعديل',
      'add': 'إضافة',
      'search': 'بحث',
      'filter': 'تصفية',
      'no_data': 'لا توجد بيانات',
      'confirm': 'تأكيد',
      'success': 'نجاح',
      'error': 'خطأ',
      
      // Payment
      'cash_on_delivery': 'الدفع عند الاستلام',
      'payment_method': 'طريقة الدفع',
      'total_amount': 'المبلغ الإجمالي',
    },
  };
}
