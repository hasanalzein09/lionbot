import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';

class RestaurantFormScreen extends StatefulWidget {
  final Map<String, dynamic>? restaurant;

  const RestaurantFormScreen({super.key, this.restaurant});

  bool get isEditing => restaurant != null;

  @override
  State<RestaurantFormScreen> createState() => _RestaurantFormScreenState();
}

class _RestaurantFormScreenState extends State<RestaurantFormScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  bool _isSaving = false;
  List<dynamic> _categories = [];

  // Form controllers
  final _nameController = TextEditingController();
  final _nameArController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _descriptionArController = TextEditingController();
  final _phoneController = TextEditingController();
  final _logoUrlController = TextEditingController();
  final _commissionController = TextEditingController();

  int? _selectedCategoryId;
  String _selectedTier = 'basic';
  bool _isActive = true;

  @override
  void initState() {
    super.initState();
    _loadCategories();
    if (widget.isEditing) {
      _populateForm();
    }
  }

  void _populateForm() {
    final r = widget.restaurant!;
    _nameController.text = r['name'] ?? '';
    _nameArController.text = r['name_ar'] ?? '';
    _descriptionController.text = r['description'] ?? '';
    _descriptionArController.text = r['description_ar'] ?? '';
    _phoneController.text = r['phone_number'] ?? '';
    _logoUrlController.text = r['logo_url'] ?? '';
    _commissionController.text = ((r['commission_rate'] ?? 0) * 100).toStringAsFixed(0);
    _selectedCategoryId = r['category_id'];
    _selectedTier = r['subscription_tier'] ?? 'basic';
    _isActive = r['is_active'] ?? true;
  }

  Future<void> _loadCategories() async {
    setState(() => _isLoading = true);
    try {
      final categories = await ApiService().getRestaurantCategories();
      if (mounted) {
        setState(() {
          _categories = categories;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _saveRestaurant() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    try {
      final data = {
        'name': _nameController.text.trim(),
        'name_ar': _nameArController.text.trim().isEmpty ? null : _nameArController.text.trim(),
        'description': _descriptionController.text.trim().isEmpty ? null : _descriptionController.text.trim(),
        'description_ar': _descriptionArController.text.trim().isEmpty ? null : _descriptionArController.text.trim(),
        'phone_number': _phoneController.text.trim().isEmpty ? null : _phoneController.text.trim(),
        'logo_url': _logoUrlController.text.trim().isEmpty ? null : _logoUrlController.text.trim(),
        'category_id': _selectedCategoryId,
        'subscription_tier': _selectedTier,
        'commission_rate': double.tryParse(_commissionController.text) != null
            ? double.parse(_commissionController.text) / 100
            : 0.0,
        'is_active': _isActive,
      };

      if (widget.isEditing) {
        await ApiService().updateRestaurant(widget.restaurant!['id'], data);
        _showSuccess('تم تحديث المطعم بنجاح');
      } else {
        await ApiService().createRestaurant(data);
        _showSuccess('تم إضافة المطعم بنجاح');
      }

      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      _showError(widget.isEditing ? 'فشل تحديث المطعم' : 'فشل إضافة المطعم');
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppTheme.errorColor),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppTheme.accentColor),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _nameArController.dispose();
    _descriptionController.dispose();
    _descriptionArController.dispose();
    _phoneController.dispose();
    _logoUrlController.dispose();
    _commissionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.isEditing ? 'تعديل المطعم' : 'إضافة مطعم'),
        centerTitle: true,
        actions: [
          if (_isSaving)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            )
          else
            IconButton(
              icon: const Icon(Icons.check),
              onPressed: _saveRestaurant,
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
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Active status switch
                    _buildSwitchTile(
                      title: 'المطعم نشط',
                      subtitle: 'يظهر للعملاء في التطبيق',
                      value: _isActive,
                      onChanged: (v) => setState(() => _isActive = v),
                    ),
                    const SizedBox(height: 24),

                    // Basic Info Section
                    _buildSectionHeader('المعلومات الأساسية'),
                    const SizedBox(height: 16),

                    _buildTextField(
                      controller: _nameController,
                      label: 'اسم المطعم (إنجليزي)',
                      hint: 'Restaurant Name',
                      required: true,
                    ),
                    const SizedBox(height: 16),

                    _buildTextField(
                      controller: _nameArController,
                      label: 'اسم المطعم (عربي)',
                      hint: 'اسم المطعم',
                    ),
                    const SizedBox(height: 16),

                    _buildTextField(
                      controller: _phoneController,
                      label: 'رقم الهاتف',
                      hint: '+961 XX XXX XXX',
                      keyboardType: TextInputType.phone,
                    ),
                    const SizedBox(height: 16),

                    _buildTextField(
                      controller: _logoUrlController,
                      label: 'رابط الشعار',
                      hint: 'https://...',
                      keyboardType: TextInputType.url,
                    ),
                    const SizedBox(height: 24),

                    // Description Section
                    _buildSectionHeader('الوصف'),
                    const SizedBox(height: 16),

                    _buildTextField(
                      controller: _descriptionController,
                      label: 'الوصف (إنجليزي)',
                      hint: 'Restaurant description...',
                      maxLines: 3,
                    ),
                    const SizedBox(height: 16),

                    _buildTextField(
                      controller: _descriptionArController,
                      label: 'الوصف (عربي)',
                      hint: 'وصف المطعم...',
                      maxLines: 3,
                    ),
                    const SizedBox(height: 24),

                    // Category & Tier Section
                    _buildSectionHeader('التصنيف والاشتراك'),
                    const SizedBox(height: 16),

                    // Category dropdown
                    _buildDropdown(
                      label: 'التصنيف',
                      value: _selectedCategoryId?.toString(),
                      items: _categories.map((c) => DropdownMenuItem(
                        value: c['id'].toString(),
                        child: Text(c['name_ar'] ?? c['name'] ?? ''),
                      )).toList(),
                      onChanged: (v) => setState(() => _selectedCategoryId = int.tryParse(v ?? '')),
                    ),
                    const SizedBox(height: 16),

                    // Subscription tier
                    _buildDropdown(
                      label: 'نوع الاشتراك',
                      value: _selectedTier,
                      items: const [
                        DropdownMenuItem(value: 'basic', child: Text('Basic')),
                        DropdownMenuItem(value: 'pro', child: Text('Pro')),
                        DropdownMenuItem(value: 'enterprise', child: Text('Enterprise')),
                      ],
                      onChanged: (v) => setState(() => _selectedTier = v ?? 'basic'),
                    ),
                    const SizedBox(height: 16),

                    // Commission rate
                    _buildTextField(
                      controller: _commissionController,
                      label: 'نسبة العمولة (%)',
                      hint: '15',
                      keyboardType: TextInputType.number,
                      suffix: const Text('%'),
                    ),
                    const SizedBox(height: 40),

                    // Save button
                    SizedBox(
                      width: double.infinity,
                      height: 54,
                      child: ElevatedButton(
                        onPressed: _isSaving ? null : _saveRestaurant,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.primaryColor,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: _isSaving
                            ? const SizedBox(
                                width: 24,
                                height: 24,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : Text(
                                widget.isEditing ? 'حفظ التغييرات' : 'إضافة المطعم',
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                      ),
                    ),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.bold,
        color: AppTheme.primaryColor,
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    String? hint,
    bool required = false,
    int maxLines = 1,
    TextInputType? keyboardType,
    Widget? suffix,
  }) {
    return TextFormField(
      controller: controller,
      maxLines: maxLines,
      keyboardType: keyboardType,
      validator: required
          ? (v) => v == null || v.trim().isEmpty ? 'هذا الحقل مطلوب' : null
          : null,
      decoration: InputDecoration(
        labelText: label + (required ? ' *' : ''),
        hintText: hint,
        suffix: suffix,
        filled: true,
        fillColor: AppTheme.cardDark,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppTheme.primaryColor),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppTheme.errorColor),
        ),
      ),
    );
  }

  Widget _buildDropdown({
    required String label,
    required String? value,
    required List<DropdownMenuItem<String>> items,
    required ValueChanged<String?> onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 14,
            color: Colors.white.withAlpha(180),
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: AppTheme.cardDark,
            borderRadius: BorderRadius.circular(12),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: value,
              isExpanded: true,
              dropdownColor: AppTheme.cardDark,
              hint: Text('اختر $label'),
              items: items,
              onChanged: onChanged,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSwitchTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.white.withAlpha(150),
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: AppTheme.accentColor,
          ),
        ],
      ),
    );
  }
}
