import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';

class MenuItemFormScreen extends StatefulWidget {
  final int? restaurantId;
  final int? categoryId;
  final Map<String, dynamic>? menuItem;

  const MenuItemFormScreen({
    super.key,
    this.restaurantId,
    this.categoryId,
    this.menuItem,
  });

  bool get isEditing => menuItem != null;

  @override
  State<MenuItemFormScreen> createState() => _MenuItemFormScreenState();
}

class _MenuItemFormScreenState extends State<MenuItemFormScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _isSaving = false;
  bool _hasVariants = false;
  List<Map<String, dynamic>> _variants = [];

  // Form controllers
  final _nameController = TextEditingController();
  final _nameArController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _descriptionArController = TextEditingController();
  final _priceController = TextEditingController();
  final _imageUrlController = TextEditingController();

  bool _isAvailable = true;
  int _order = 0;

  @override
  void initState() {
    super.initState();
    if (widget.isEditing) {
      _populateForm();
    }
  }

  void _populateForm() {
    final item = widget.menuItem!;
    _nameController.text = item['name'] ?? '';
    _nameArController.text = item['name_ar'] ?? '';
    _descriptionController.text = item['description'] ?? '';
    _descriptionArController.text = item['description_ar'] ?? '';
    _priceController.text = (item['price'] ?? 0).toString();
    _imageUrlController.text = item['image_url'] ?? '';
    _isAvailable = item['is_available'] ?? true;
    _order = item['order'] ?? 0;
    _hasVariants = item['has_variants'] ?? false;

    // Load variants if exists
    if (item['variants'] != null) {
      _variants = List<Map<String, dynamic>>.from(
        (item['variants'] as List).map((v) => {
          'id': v['id'],
          'name': v['name'] ?? '',
          'name_ar': v['name_ar'] ?? '',
          'price': v['price'] ?? 0,
        }),
      );
    }
  }

  Future<void> _saveMenuItem() async {
    if (!_formKey.currentState!.validate()) return;

    if (_hasVariants && _variants.isEmpty) {
      _showError('يجب إضافة متغير واحد على الأقل');
      return;
    }

    setState(() => _isSaving = true);

    try {
      final data = {
        'name': _nameController.text.trim(),
        'name_ar': _nameArController.text.trim().isEmpty ? null : _nameArController.text.trim(),
        'description': _descriptionController.text.trim().isEmpty ? null : _descriptionController.text.trim(),
        'description_ar': _descriptionArController.text.trim().isEmpty ? null : _descriptionArController.text.trim(),
        'price': _hasVariants ? null : double.tryParse(_priceController.text) ?? 0,
        'image_url': _imageUrlController.text.trim().isEmpty ? null : _imageUrlController.text.trim(),
        'is_available': _isAvailable,
        'order': _order,
        'category_id': widget.categoryId,
        'has_variants': _hasVariants,
        if (_hasVariants) 'variants': _variants,
      };

      if (widget.isEditing) {
        await ApiService().updateMenuItem(widget.menuItem!['id'], data);
        _showSuccess('تم تحديث الصنف بنجاح');
      } else {
        await ApiService().createMenuItem(data);
        _showSuccess('تم إضافة الصنف بنجاح');
      }

      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      _showError(widget.isEditing ? 'فشل تحديث الصنف' : 'فشل إضافة الصنف');
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

  void _addVariant() {
    setState(() {
      _variants.add({
        'name': '',
        'name_ar': '',
        'price': 0.0,
      });
    });
  }

  void _removeVariant(int index) {
    setState(() {
      _variants.removeAt(index);
    });
  }

  @override
  void dispose() {
    _nameController.dispose();
    _nameArController.dispose();
    _descriptionController.dispose();
    _descriptionArController.dispose();
    _priceController.dispose();
    _imageUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.isEditing ? 'تعديل الصنف' : 'إضافة صنف'),
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
              onPressed: _saveMenuItem,
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Available switch
              _buildSwitchTile(
                title: 'متوفر',
                subtitle: 'يظهر للعملاء في القائمة',
                value: _isAvailable,
                onChanged: (v) => setState(() => _isAvailable = v),
              ),
              const SizedBox(height: 24),

              // Basic Info
              _buildSectionHeader('المعلومات الأساسية'),
              const SizedBox(height: 16),

              _buildTextField(
                controller: _nameController,
                label: 'اسم الصنف (إنجليزي)',
                hint: 'Item Name',
                required: true,
              ),
              const SizedBox(height: 16),

              _buildTextField(
                controller: _nameArController,
                label: 'اسم الصنف (عربي)',
                hint: 'اسم الصنف',
              ),
              const SizedBox(height: 16),

              _buildTextField(
                controller: _imageUrlController,
                label: 'رابط الصورة',
                hint: 'https://...',
                keyboardType: TextInputType.url,
              ),
              const SizedBox(height: 24),

              // Description
              _buildSectionHeader('الوصف'),
              const SizedBox(height: 16),

              _buildTextField(
                controller: _descriptionController,
                label: 'الوصف (إنجليزي)',
                hint: 'Item description...',
                maxLines: 3,
              ),
              const SizedBox(height: 16),

              _buildTextField(
                controller: _descriptionArController,
                label: 'الوصف (عربي)',
                hint: 'وصف الصنف...',
                maxLines: 3,
              ),
              const SizedBox(height: 24),

              // Pricing
              _buildSectionHeader('التسعير'),
              const SizedBox(height: 16),

              // Variants switch
              _buildSwitchTile(
                title: 'متغيرات (أحجام)',
                subtitle: 'تفعيل أحجام مختلفة مثل صغير، وسط، كبير',
                value: _hasVariants,
                onChanged: (v) => setState(() => _hasVariants = v),
              ),
              const SizedBox(height: 16),

              if (!_hasVariants) ...[
                _buildTextField(
                  controller: _priceController,
                  label: 'السعر',
                  hint: '0.00',
                  required: true,
                  keyboardType: TextInputType.number,
                  prefix: const Text('\$ '),
                ),
              ] else ...[
                // Variants list
                _buildVariantsList(),
              ],

              const SizedBox(height: 40),

              // Save button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: _isSaving ? null : _saveMenuItem,
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
                          widget.isEditing ? 'حفظ التغييرات' : 'إضافة الصنف',
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

  Widget _buildVariantsList() {
    return Column(
      children: [
        ...List.generate(_variants.length, (index) {
          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.cardDark,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.primaryColor.withAlpha(50)),
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    Text(
                      'متغير ${index + 1}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.delete, color: AppTheme.errorColor),
                      onPressed: () => _removeVariant(index),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        initialValue: _variants[index]['name'],
                        decoration: const InputDecoration(
                          labelText: 'الاسم (EN)',
                          hintText: 'Small',
                          isDense: true,
                        ),
                        onChanged: (v) => _variants[index]['name'] = v,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        initialValue: _variants[index]['name_ar'],
                        decoration: const InputDecoration(
                          labelText: 'الاسم (AR)',
                          hintText: 'صغير',
                          isDense: true,
                        ),
                        onChanged: (v) => _variants[index]['name_ar'] = v,
                      ),
                    ),
                    const SizedBox(width: 12),
                    SizedBox(
                      width: 100,
                      child: TextFormField(
                        initialValue: _variants[index]['price'].toString(),
                        decoration: const InputDecoration(
                          labelText: 'السعر',
                          prefixText: '\$ ',
                          isDense: true,
                        ),
                        keyboardType: TextInputType.number,
                        onChanged: (v) => _variants[index]['price'] = double.tryParse(v) ?? 0,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          );
        }),
        const SizedBox(height: 8),
        OutlinedButton.icon(
          onPressed: _addVariant,
          icon: const Icon(Icons.add),
          label: const Text('إضافة متغير'),
          style: OutlinedButton.styleFrom(
            foregroundColor: AppTheme.primaryColor,
            side: const BorderSide(color: AppTheme.primaryColor),
          ),
        ),
      ],
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
    Widget? prefix,
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
        prefixIcon: prefix != null
            ? Padding(padding: const EdgeInsets.only(left: 12), child: prefix)
            : null,
        prefixIconConstraints: const BoxConstraints(minWidth: 0, minHeight: 0),
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
