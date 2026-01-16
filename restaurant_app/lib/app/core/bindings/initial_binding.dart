import 'package:get/get.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

class InitialBinding extends Bindings {
  @override
  void dependencies() {
    // Services
    Get.put(StorageService(), permanent: true);
    Get.put(ApiService(), permanent: true);
  }
}
