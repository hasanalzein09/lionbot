import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Reusable error display widget with retry functionality
class AppErrorWidget extends StatelessWidget {
  final String message;
  final String? details;
  final VoidCallback? onRetry;
  final IconData icon;

  const AppErrorWidget({
    super.key,
    required this.message,
    this.details,
    this.onRetry,
    this.icon = Icons.error_outline,
  });

  /// Factory for network errors
  factory AppErrorWidget.network({VoidCallback? onRetry}) {
    return AppErrorWidget(
      message: 'Connection Error',
      details: 'Please check your internet connection and try again.',
      icon: Icons.wifi_off,
      onRetry: onRetry,
    );
  }

  /// Factory for server errors
  factory AppErrorWidget.server({VoidCallback? onRetry}) {
    return AppErrorWidget(
      message: 'Server Error',
      details: 'Something went wrong on our end. Please try again later.',
      icon: Icons.cloud_off,
      onRetry: onRetry,
    );
  }

  /// Factory for empty state
  factory AppErrorWidget.empty({
    required String message,
    IconData icon = Icons.inbox_outlined,
  }) {
    return AppErrorWidget(
      message: message,
      icon: icon,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 64,
              color: AppTheme.errorColor.withOpacity(0.7),
            ),
            const SizedBox(height: 16),
            Text(
              message,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
              textAlign: TextAlign.center,
            ),
            if (details != null) ...[
              const SizedBox(height: 8),
              Text(
                details!,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.white.withOpacity(0.6),
                ),
                textAlign: TextAlign.center,
              ),
            ],
            if (onRetry != null) ...[
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh, size: 18),
                label: const Text('Try Again'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Loading state widget
class AppLoadingWidget extends StatelessWidget {
  final String? message;

  const AppLoadingWidget({super.key, this.message});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(
            color: AppTheme.primaryColor,
            strokeWidth: 3,
          ),
          if (message != null) ...[
            const SizedBox(height: 16),
            Text(
              message!,
              style: TextStyle(
                color: Colors.white.withOpacity(0.6),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

/// Async content builder with loading/error states
class AsyncContent<T> extends StatelessWidget {
  final Future<T>? future;
  final T? data;
  final bool isLoading;
  final String? error;
  final Widget Function(T data) builder;
  final VoidCallback? onRetry;
  final String? loadingMessage;

  const AsyncContent({
    super.key,
    this.future,
    this.data,
    this.isLoading = false,
    this.error,
    required this.builder,
    this.onRetry,
    this.loadingMessage,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return AppLoadingWidget(message: loadingMessage);
    }

    if (error != null) {
      return AppErrorWidget(
        message: 'Error',
        details: error,
        onRetry: onRetry,
      );
    }

    if (data != null) {
      return builder(data as T);
    }

    if (future != null) {
      return FutureBuilder<T>(
        future: future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return AppLoadingWidget(message: loadingMessage);
          }

          if (snapshot.hasError) {
            return AppErrorWidget(
              message: 'Error',
              details: snapshot.error.toString(),
              onRetry: onRetry,
            );
          }

          if (snapshot.hasData) {
            return builder(snapshot.data as T);
          }

          return const AppLoadingWidget();
        },
      );
    }

    return const AppLoadingWidget();
  }
}
