import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';

class UserFormScreen extends StatefulWidget {
  final Map<String, dynamic>? user;
  
  const UserFormScreen({super.key, this.user});

  @override
  State<UserFormScreen> createState() => _UserFormScreenState();
}

class _UserFormScreenState extends State<UserFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  
  String _selectedRole = 'user';
  int? _selectedRestaurant;
  bool _isActive = true;
  bool _isLoading = false;
  bool _obscurePassword = true;
  
  List<dynamic> _restaurants = [];

  bool get _isEditing => widget.user != null;

  @override
  void initState() {
    super.initState();
    if (_isEditing) {
      _nameController.text = widget.user!['full_name'] ?? '';
      _emailController.text = widget.user!['email'] ?? '';
      _phoneController.text = widget.user!['phone_number'] ?? '';
      _selectedRole = widget.user!['role'] ?? 'user';
      _selectedRestaurant = widget.user!['restaurant_id'];
      _isActive = widget.user!['is_active'] ?? true;
    }
    _loadRestaurants();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _loadRestaurants() async {
    try {
      final restaurants = await ApiService().getRestaurants();
      if (mounted) setState(() => _restaurants = restaurants);
    } catch (e) {
      // Ignore errors
    }
  }

  Future<void> _saveUser() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final data = {
        'full_name': _nameController.text.trim(),
        'email': _emailController.text.trim().isEmpty ? null : _emailController.text.trim(),
        'phone_number': _phoneController.text.trim(),
        'role': _selectedRole,
        'is_active': _isActive,
      };

      if (_selectedRole == 'restaurant_owner' && _selectedRestaurant != null) {
        data['restaurant_id'] = _selectedRestaurant;
      }

      if (!_isEditing || _passwordController.text.isNotEmpty) {
        if (_passwordController.text.isNotEmpty) {
          data['password'] = _passwordController.text;
        }
      }

      if (_isEditing) {
        await ApiService().updateUser(widget.user!['id'], data);
      } else {
        if (_passwordController.text.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Password is required for new users'), backgroundColor: AppTheme.errorColor),
          );
          setState(() => _isLoading = false);
          return;
        }
        await ApiService().createUser(data);
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('User ${_isEditing ? 'updated' : 'created'} successfully'),
            backgroundColor: AppTheme.accentColor,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${e.toString()}'), backgroundColor: AppTheme.errorColor),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Edit User' : 'New User'),
        actions: [
          if (!_isLoading)
            TextButton(
              onPressed: _saveUser,
              child: const Text(
                'SAVE',
                style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold),
              ),
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryColor))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Avatar
                    Center(
                      child: Stack(
                        children: [
                          CircleAvatar(
                            radius: 50,
                            backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
                            child: Icon(
                              _getRoleIcon(_selectedRole),
                              size: 50,
                              color: AppTheme.primaryColor,
                            ),
                          ),
                          Positioned(
                            bottom: 0,
                            right: 0,
                            child: Container(
                              padding: const EdgeInsets.all(4),
                              decoration: const BoxDecoration(
                                color: AppTheme.primaryColor,
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.camera_alt, size: 20, color: Colors.black),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 32),

                    // Full Name
                    _buildSectionHeader('Basic Information'),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _nameController,
                      style: const TextStyle(color: Colors.white),
                      decoration: const InputDecoration(
                        labelText: 'Full Name *',
                        prefixIcon: Icon(Icons.person, color: AppTheme.textMuted),
                      ),
                      validator: (v) => v?.isEmpty == true ? 'Name is required' : null,
                    ),
                    const SizedBox(height: 16),

                    // Phone Number
                    TextFormField(
                      controller: _phoneController,
                      style: const TextStyle(color: Colors.white),
                      keyboardType: TextInputType.phone,
                      decoration: const InputDecoration(
                        labelText: 'Phone Number *',
                        prefixIcon: Icon(Icons.phone, color: AppTheme.textMuted),
                        hintText: '+961 XX XXX XXX',
                      ),
                      validator: (v) => v?.isEmpty == true ? 'Phone is required' : null,
                    ),
                    const SizedBox(height: 16),

                    // Email
                    TextFormField(
                      controller: _emailController,
                      style: const TextStyle(color: Colors.white),
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(
                        labelText: 'Email (optional)',
                        prefixIcon: Icon(Icons.email, color: AppTheme.textMuted),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Password
                    _buildSectionHeader('Security'),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _passwordController,
                      style: const TextStyle(color: Colors.white),
                      obscureText: _obscurePassword,
                      decoration: InputDecoration(
                        labelText: _isEditing ? 'New Password (leave empty to keep)' : 'Password *',
                        prefixIcon: const Icon(Icons.lock, color: AppTheme.textMuted),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePassword ? Icons.visibility_off : Icons.visibility,
                            color: AppTheme.textMuted,
                          ),
                          onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Role
                    _buildSectionHeader('Role & Permissions'),
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      decoration: BoxDecoration(
                        color: AppTheme.surfaceDark,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: DropdownButtonFormField<String>(
                        value: _selectedRole,
                        dropdownColor: AppTheme.cardDark,
                        style: const TextStyle(color: Colors.white),
                        decoration: const InputDecoration(
                          border: InputBorder.none,
                          labelText: 'Role',
                        ),
                        items: const [
                          DropdownMenuItem(value: 'user', child: Text('Customer')),
                          DropdownMenuItem(value: 'driver', child: Text('Driver')),
                          DropdownMenuItem(value: 'restaurant_owner', child: Text('Restaurant Owner')),
                          DropdownMenuItem(value: 'admin', child: Text('Admin')),
                          DropdownMenuItem(value: 'super_admin', child: Text('Super Admin')),
                        ],
                        onChanged: (v) => setState(() => _selectedRole = v ?? 'user'),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Restaurant (for restaurant_owner)
                    if (_selectedRole == 'restaurant_owner') ...[
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        decoration: BoxDecoration(
                          color: AppTheme.surfaceDark,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: DropdownButtonFormField<int>(
                          value: _selectedRestaurant,
                          dropdownColor: AppTheme.cardDark,
                          style: const TextStyle(color: Colors.white),
                          decoration: const InputDecoration(
                            border: InputBorder.none,
                            labelText: 'Assigned Restaurant',
                          ),
                          items: _restaurants.map((r) => DropdownMenuItem(
                            value: r['id'] as int,
                            child: Text(r['name'] ?? 'Unknown'),
                          )).toList(),
                          onChanged: (v) => setState(() => _selectedRestaurant = v),
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // Active status
                    Container(
                      decoration: BoxDecoration(
                        color: AppTheme.surfaceDark,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: SwitchListTile(
                        title: const Text('Active', style: TextStyle(color: Colors.white)),
                        subtitle: Text(
                          _isActive ? 'User can access the system' : 'User is suspended',
                          style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 12),
                        ),
                        value: _isActive,
                        onChanged: (v) => setState(() => _isActive = v),
                        activeColor: AppTheme.accentColor,
                      ),
                    ),
                    const SizedBox(height: 32),

                    // Save button
                    ElevatedButton(
                      onPressed: _isLoading ? null : _saveUser,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: Text(
                        _isEditing ? 'UPDATE USER' : 'CREATE USER',
                        style: const TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1),
                      ),
                    ),
                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Text(
      title,
      style: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: Colors.white.withOpacity(0.5),
        letterSpacing: 1,
      ),
    );
  }

  IconData _getRoleIcon(String role) {
    switch (role) {
      case 'super_admin':
      case 'admin':
        return Icons.admin_panel_settings;
      case 'restaurant_owner':
        return Icons.restaurant;
      case 'driver':
        return Icons.delivery_dining;
      default:
        return Icons.person;
    }
  }
}
