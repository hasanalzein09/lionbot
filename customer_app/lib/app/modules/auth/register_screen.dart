import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';
import '../../routes/app_routes.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    try {
      await ApiService().register(_nameController.text, _phoneController.text, _passwordController.text);
      Get.snackbar('success'.tr, 'Account created! Please login.');
      Get.offNamed(AppRoutes.login);
    } catch (e) {
      Get.snackbar('error'.tr, 'Registration failed');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('register'.tr)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 20),
              TextFormField(
                controller: _nameController,
                decoration: InputDecoration(labelText: 'name'.tr, prefixIcon: const Icon(Icons.person)),
                validator: (v) => v?.isEmpty ?? true ? 'required'.tr : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                decoration: InputDecoration(labelText: 'phone'.tr, prefixIcon: const Icon(Icons.phone)),
                validator: (v) => v?.isEmpty ?? true ? 'required'.tr : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _passwordController,
                obscureText: true,
                decoration: InputDecoration(labelText: 'password'.tr, prefixIcon: const Icon(Icons.lock)),
                validator: (v) => v != null && v.length < 6 ? 'Min 6 characters' : null,
              ),
              const SizedBox(height: 32),
              SizedBox(
                height: 56,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _register,
                  child: _isLoading
                      ? const CircularProgressIndicator(strokeWidth: 2, color: Colors.white)
                      : Text('sign_up'.tr),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
