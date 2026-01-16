import '../config/app_config.dart';

/// Form validation utilities for consistent validation across the app.
class Validators {
  Validators._();

  /// Validate email format
  static String? email(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email is required';
    }

    final emailRegex = RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    );

    if (!emailRegex.hasMatch(value.trim())) {
      return 'Please enter a valid email address';
    }

    return null;
  }

  /// Validate phone number format
  static String? phoneNumber(String? value) {
    if (value == null || value.isEmpty) {
      return 'Phone number is required';
    }

    // Remove common formatting characters
    final cleaned = value.replaceAll(RegExp(r'[\s\-\(\)]'), '');

    // Should start with + or digit and be 8-15 digits
    final phoneRegex = RegExp(r'^\+?[0-9]{8,15}$');

    if (!phoneRegex.hasMatch(cleaned)) {
      return 'Please enter a valid phone number';
    }

    return null;
  }

  /// Validate required field
  static String? required(String? value, [String fieldName = 'This field']) {
    if (value == null || value.trim().isEmpty) {
      return '$fieldName is required';
    }
    return null;
  }

  /// Validate password strength
  static String? password(String? value) {
    if (value == null || value.isEmpty) {
      return 'Password is required';
    }

    if (value.length < AppConfig.minPasswordLength) {
      return 'Password must be at least ${AppConfig.minPasswordLength} characters';
    }

    // Check for at least one uppercase letter
    if (!RegExp(r'[A-Z]').hasMatch(value)) {
      return 'Password must contain at least one uppercase letter';
    }

    // Check for at least one lowercase letter
    if (!RegExp(r'[a-z]').hasMatch(value)) {
      return 'Password must contain at least one lowercase letter';
    }

    // Check for at least one digit
    if (!RegExp(r'[0-9]').hasMatch(value)) {
      return 'Password must contain at least one number';
    }

    return null;
  }

  /// Validate password confirmation matches
  static String? confirmPassword(String? value, String? password) {
    if (value == null || value.isEmpty) {
      return 'Please confirm your password';
    }

    if (value != password) {
      return 'Passwords do not match';
    }

    return null;
  }

  /// Validate URL format
  static String? url(String? value, {bool required = false}) {
    if (value == null || value.isEmpty) {
      return required ? 'URL is required' : null;
    }

    final urlRegex = RegExp(
      r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
    );

    if (!urlRegex.hasMatch(value.trim())) {
      return 'Please enter a valid URL';
    }

    return null;
  }

  /// Validate numeric value
  static String? number(String? value, {
    bool required = false,
    double? min,
    double? max,
    String fieldName = 'Value',
  }) {
    if (value == null || value.isEmpty) {
      return required ? '$fieldName is required' : null;
    }

    final number = double.tryParse(value);
    if (number == null) {
      return 'Please enter a valid number';
    }

    if (min != null && number < min) {
      return '$fieldName must be at least $min';
    }

    if (max != null && number > max) {
      return '$fieldName must not exceed $max';
    }

    return null;
  }

  /// Validate positive number (price, quantity, etc.)
  static String? positiveNumber(String? value, {
    bool required = false,
    String fieldName = 'Value',
  }) {
    return number(value, required: required, min: 0, fieldName: fieldName);
  }

  /// Validate integer value
  static String? integer(String? value, {
    bool required = false,
    int? min,
    int? max,
    String fieldName = 'Value',
  }) {
    if (value == null || value.isEmpty) {
      return required ? '$fieldName is required' : null;
    }

    final intValue = int.tryParse(value);
    if (intValue == null) {
      return 'Please enter a whole number';
    }

    if (min != null && intValue < min) {
      return '$fieldName must be at least $min';
    }

    if (max != null && intValue > max) {
      return '$fieldName must not exceed $max';
    }

    return null;
  }

  /// Validate percentage (0-100)
  static String? percentage(String? value, {bool required = false}) {
    return number(
      value,
      required: required,
      min: 0,
      max: 100,
      fieldName: 'Percentage',
    );
  }

  /// Validate min length
  static String? minLength(String? value, int length, [String fieldName = 'This field']) {
    if (value == null || value.length < length) {
      return '$fieldName must be at least $length characters';
    }
    return null;
  }

  /// Validate max length
  static String? maxLength(String? value, int length, [String fieldName = 'This field']) {
    if (value != null && value.length > length) {
      return '$fieldName must not exceed $length characters';
    }
    return null;
  }

  /// Validate length range
  static String? lengthRange(String? value, int min, int max, [String fieldName = 'This field']) {
    if (value == null || value.isEmpty) {
      return '$fieldName is required';
    }

    if (value.length < min) {
      return '$fieldName must be at least $min characters';
    }

    if (value.length > max) {
      return '$fieldName must not exceed $max characters';
    }

    return null;
  }

  /// Combine multiple validators
  static String? combine(String? value, List<String? Function(String?)> validators) {
    for (final validator in validators) {
      final result = validator(value);
      if (result != null) {
        return result;
      }
    }
    return null;
  }
}

/// Extension for easier validator usage
extension ValidatorExtension on String? {
  String? validateEmail() => Validators.email(this);
  String? validatePhone() => Validators.phoneNumber(this);
  String? validateRequired([String fieldName = 'This field']) =>
      Validators.required(this, fieldName);
  String? validatePassword() => Validators.password(this);
  String? validateUrl({bool required = false}) =>
      Validators.url(this, required: required);
}
