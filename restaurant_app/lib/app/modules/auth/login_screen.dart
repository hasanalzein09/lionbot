import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:dio/dio.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/notification_service.dart';
import '../../routes/app_routes.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true;
  String? _error;

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() { _isLoading = true; _error = null; });

    try {
      final dio = Dio(BaseOptions(
        baseUrl: 'https://lionbot-backend-426202982674.me-west1.run.app/api/v1',
      ));
      
      final response = await dio.post(
        '/login/access-token/',
        data: FormData.fromMap({
          'username': _usernameController.text.trim(),
          'password': _passwordController.text,
          'grant_type': 'password',
        }),
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );

      final token = response.data['access_token'] as String;
      await const FlutterSecureStorage().write(key: 'token', value: token);
      
      // Get user info to get restaurant_id
      dio.options.headers['Authorization'] = 'Bearer $token';
      final userResponse = await dio.get('/users/me/');
      final restaurantId = userResponse.data['restaurant_id'];
      
      if (restaurantId != null) {
        await NotificationService().subscribeToRestaurant(restaurantId);
        await const FlutterSecureStorage().write(key: 'restaurant_id', value: restaurantId.toString());
      }

      if (mounted) {
        Navigator.pushReplacementNamed(context, AppRoutes.home);
      }
    } catch (e) {
      setState(() {
        _error = 'Login failed. Please check your credentials.';
      });
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Container(
                    width: 100, height: 100,
                    margin: const EdgeInsets.only(bottom: 32),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(colors: [AppTheme.primaryColor, AppTheme.primaryColor.withOpacity(0.7)]),
                      borderRadius: BorderRadius.circular(25),
                    ),
                    child: const Icon(Icons.restaurant_menu, size: 50, color: Colors.white),
                  ),
                  const Text('Restaurant Login', textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text('Sign in to manage your orders', textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.white.withOpacity(0.6))),
                  const SizedBox(height: 40),
                  
                  if (_error != null) ...[
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppTheme.errorColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(_error!, style: const TextStyle(color: AppTheme.errorColor)),
                    ),
                    const SizedBox(height: 16),
                  ],
                  
                  TextFormField(
                    controller: _usernameController,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Email or Phone',
                      prefixIcon: Icon(Icons.person_outline, color: Colors.white.withOpacity(0.5)),
                    ),
                    validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                  ),
                  const SizedBox(height: 16),
                  
                  TextFormField(
                    controller: _passwordController,
                    obscureText: _obscurePassword,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Password',
                      prefixIcon: Icon(Icons.lock_outline, color: Colors.white.withOpacity(0.5)),
                      suffixIcon: IconButton(
                        icon: Icon(_obscurePassword ? Icons.visibility_off : Icons.visibility,
                          color: Colors.white.withOpacity(0.5)),
                        onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                      ),
                    ),
                    validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                  ),
                  const SizedBox(height: 32),
                  
                  SizedBox(
                    height: 56,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _login,
                      child: _isLoading
                          ? const SizedBox(width: 24, height: 24,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Text('SIGN IN', style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
