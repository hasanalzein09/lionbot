import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:lionbot_mobile/app/data/services/api_service.dart';
import 'package:lionbot_mobile/app/data/services/location_service.dart';
import 'package:lionbot_mobile/app/data/services/local_storage_service.dart';

/// User model
class UserModel {
  final int id;
  final String fullName;
  final String email;
  final String phoneNumber;
  final String role;
  final bool isActive;

  UserModel({
    required this.id,
    required this.fullName,
    required this.email,
    required this.phoneNumber,
    required this.role,
    required this.isActive,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as int,
      fullName: json['full_name'] as String,
      email: json['email'] as String,
      phoneNumber: json['phone_number'] as String,
      role: json['role'] as String,
      isActive: json['is_active'] as bool,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'full_name': fullName,
    'email': email,
    'phone_number': phoneNumber,
    'role': role,
    'is_active': isActive,
  };

  bool get isDriver => role == 'driver';
}

/// Auth state
class AuthState {
  final UserModel? user;
  final bool isLoading;
  final bool isAuthenticated;
  final String? error;

  AuthState({
    this.user,
    this.isLoading = false,
    this.isAuthenticated = false,
    this.error,
  });

  AuthState copyWith({
    UserModel? user,
    bool? isLoading,
    bool? isAuthenticated,
    String? error,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      error: error,
    );
  }
}

/// Auth Notifier
class AuthNotifier extends StateNotifier<AuthState> {
  final ApiService _api;
  final LocationService _locationService;
  final LocalStorageService _localStorage;
  final FlutterSecureStorage _secureStorage;

  AuthNotifier(
    this._api,
    this._locationService,
    this._localStorage,
    this._secureStorage,
  ) : super(AuthState()) {
    _checkExistingAuth();
  }

  Future<void> _checkExistingAuth() async {
    final token = await _secureStorage.read(key: 'token');
    if (token != null) {
      // Try to restore session
      final cachedUser = _localStorage.getCachedUser();
      if (cachedUser != null) {
        state = state.copyWith(
          user: UserModel.fromJson(cachedUser),
          isAuthenticated: true,
        );
        
        // Start location tracking if driver
        if (cachedUser['role'] == 'driver') {
          _locationService.startTracking(cachedUser['id']);
        }
      }
    }
  }

  Future<bool> login(String phone, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final response = await _api.client.post(
        '/login/access-token',
        data: {
          'username': phone,
          'password': password,
          'grant_type': 'password',
        },
      );
      
      final token = response.data['access_token'] as String;
      await _secureStorage.write(key: 'token', value: token);
      
      // Fetch user info
      final userResponse = await _api.client.get('/users/me');
      final user = UserModel.fromJson(userResponse.data);
      
      // Cache user
      await _localStorage.cacheUser(user.toJson());
      await _localStorage.setLastLoginPhone(phone);
      
      state = state.copyWith(
        user: user,
        isAuthenticated: true,
        isLoading: false,
      );
      
      // Start location tracking for drivers
      if (user.isDriver) {
        _locationService.startTracking(user.id);
      }
      
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Login failed: ${e.toString()}',
      );
      return false;
    }
  }

  Future<void> logout() async {
    _locationService.stopTracking();
    await _secureStorage.delete(key: 'token');
    await _localStorage.clearUserCache();
    
    state = AuthState();
  }
}

/// Auth provider
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final api = ApiService();
  final locationService = LocationService();
  final localStorage = ref.watch(localStorageProvider);
  const secureStorage = FlutterSecureStorage();
  
  return AuthNotifier(api, locationService, localStorage, secureStorage);
});

/// Current user provider
final currentUserProvider = Provider<UserModel?>((ref) {
  return ref.watch(authProvider).user;
});

/// Is driver provider
final isDriverProvider = Provider<bool>((ref) {
  return ref.watch(currentUserProvider)?.isDriver ?? false;
});
