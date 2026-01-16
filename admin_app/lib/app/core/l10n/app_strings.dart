/// Application string constants for localization
/// Currently supports English only, can be extended for Arabic
class AppStrings {
  // General
  static const String appName = 'Lion Admin';
  static const String loading = 'Loading...';
  static const String error = 'Error';
  static const String success = 'Success';
  static const String cancel = 'Cancel';
  static const String save = 'Save';
  static const String delete = 'Delete';
  static const String edit = 'Edit';
  static const String add = 'Add';
  static const String search = 'Search';
  static const String refresh = 'Refresh';
  static const String tryAgain = 'Try Again';
  static const String noData = 'No data available';

  // Auth
  static const String login = 'Login';
  static const String logout = 'Logout';
  static const String email = 'Email';
  static const String password = 'Password';
  static const String forgotPassword = 'Forgot Password?';
  static const String loginFailed = 'Login failed. Please check your credentials.';
  static const String accessDenied = 'Access denied. Admin privileges required.';

  // Navigation
  static const String dashboard = 'Dashboard';
  static const String orders = 'Orders';
  static const String restaurants = 'Restaurants';
  static const String drivers = 'Drivers';
  static const String settings = 'Settings';
  static const String customers = 'Customers';

  // Orders
  static const String allOrders = 'All Orders';
  static const String pendingOrders = 'Pending';
  static const String preparingOrders = 'Preparing';
  static const String deliveryOrders = 'Out for Delivery';
  static const String completedOrders = 'Completed';
  static const String cancelledOrders = 'Cancelled';
  static const String noOrders = 'No orders found';
  static const String orderDetails = 'Order Details';
  static const String updateStatus = 'Update Status';
  static const String assignDriver = 'Assign Driver';

  // Order Status
  static const String statusPending = 'Pending';
  static const String statusConfirmed = 'Confirmed';
  static const String statusPreparing = 'Preparing';
  static const String statusReady = 'Ready';
  static const String statusOutForDelivery = 'Out for Delivery';
  static const String statusDelivered = 'Delivered';
  static const String statusCancelled = 'Cancelled';

  // Restaurants
  static const String addRestaurant = 'Add Restaurant';
  static const String editRestaurant = 'Edit Restaurant';
  static const String restaurantName = 'Restaurant Name';
  static const String restaurantDescription = 'Description';
  static const String noRestaurants = 'No restaurants found';

  // Menu
  static const String menuItems = 'Menu Items';
  static const String addMenuItem = 'Add Item';
  static const String editMenuItem = 'Edit Item';
  static const String itemName = 'Item Name';
  static const String itemPrice = 'Price';
  static const String itemDescription = 'Description';
  static const String categories = 'Categories';
  static const String addCategory = 'Add Category';

  // Drivers
  static const String noDrivers = 'No drivers found';
  static const String driverOnline = 'Online';
  static const String driverOffline = 'Offline';
  static const String activeDeliveries = 'Active Deliveries';

  // Settings
  static const String generalSettings = 'General Settings';
  static const String notifications = 'Notifications';
  static const String account = 'Account';
  static const String about = 'About';

  // Errors
  static const String networkError = 'Connection error. Please check your internet.';
  static const String serverError = 'Server error. Please try again later.';
  static const String unknownError = 'An unexpected error occurred.';

  // Confirmations
  static const String confirmDelete = 'Are you sure you want to delete this?';
  static const String confirmLogout = 'Are you sure you want to logout?';

  /// Get status display text
  static String getStatusText(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return statusPending;
      case 'confirmed':
        return statusConfirmed;
      case 'preparing':
        return statusPreparing;
      case 'ready':
        return statusReady;
      case 'out_for_delivery':
        return statusOutForDelivery;
      case 'delivered':
        return statusDelivered;
      case 'cancelled':
        return statusCancelled;
      default:
        return status;
    }
  }
}
