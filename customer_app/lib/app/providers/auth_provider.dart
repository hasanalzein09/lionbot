import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../core/services/api_service.dart';
import '../core/services/notification_service.dart';

// User Model
class UserModel {
  final int id;
  final String fullName;
  final String phoneNumber;
  final String? email;
  final String role;
  final bool isActive;

  UserModel({
    required this.id,
    required this.fullName,
    required this.phoneNumber,
    this.email,
    required this.role,
    required this.isActive,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      fullName: json['full_name'] ?? '',
      phoneNumber: json['phone_number'] ?? '',
      email: json['email'],
      role: json['role'] ?? 'customer',
      isActive: json['is_active'] ?? true,
    );
  }
}

// Auth State
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

// Auth Notifier
class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(AuthState());

  final _api = ApiService();
  final _storage = const FlutterSecureStorage();

  Future<bool> login(String phone, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _api.login(phone, password);
      await _storage.write(key: 'token', value: response['access_token']);
      
      final user = await _api.getCurrentUser();
      final userModel = UserModel.fromJson(user);
      
      // Subscribe to notifications
      await NotificationService().subscribeToUser(userModel.id);
      
      state = AuthState(
        user: userModel,
        isAuthenticated: true,
        isLoading: false,
      );
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }

  Future<bool> register(String name, String phone, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _api.register(name, phone, password);
      state = state.copyWith(isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }

  Future<void> loadUser() async {
    final token = await _storage.read(key: 'token');
    if (token == null) return;

    state = state.copyWith(isLoading: true);
    try {
      final user = await _api.getCurrentUser();
      state = AuthState(
        user: UserModel.fromJson(user),
        isAuthenticated: true,
        isLoading: false,
      );
    } catch (e) {
      await logout();
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: 'token');
    state = AuthState();
  }
}

// Provider
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});
