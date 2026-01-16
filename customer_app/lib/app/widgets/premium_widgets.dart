import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';

/// Premium star rating widget
class StarRating extends StatelessWidget {
  final double rating;
  final int reviewCount;
  final double size;
  final bool showCount;

  const StarRating({
    super.key,
    required this.rating,
    this.reviewCount = 0,
    this.size = 16,
    this.showCount = true,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        ...List.generate(5, (index) {
          final filled = index < rating.floor();
          final half = index == rating.floor() && rating % 1 >= 0.5;
          return Icon(
            half ? Icons.star_half : (filled ? Icons.star : Icons.star_border),
            color: Colors.amber,
            size: size,
          );
        }),
        const SizedBox(width: 4),
        Text(
          rating.toStringAsFixed(1),
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: size * 0.85),
        ),
        if (showCount && reviewCount > 0) ...[
          const SizedBox(width: 4),
          Text(
            '($reviewCount)',
            style: TextStyle(color: Colors.grey[600], fontSize: size * 0.75),
          ),
        ],
      ],
    );
  }
}


/// Animated loading skeleton
class SkeletonLoader extends StatefulWidget {
  final double width;
  final double height;
  final double borderRadius;

  const SkeletonLoader({
    super.key,
    required this.width,
    required this.height,
    this.borderRadius = 8,
  });

  @override
  State<SkeletonLoader> createState() => _SkeletonLoaderState();
}

class _SkeletonLoaderState extends State<SkeletonLoader>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();
    _animation = Tween<double>(begin: -2, end: 2).animate(_controller);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(widget.borderRadius),
            gradient: LinearGradient(
              begin: Alignment(_animation.value - 1, 0),
              end: Alignment(_animation.value + 1, 0),
              colors: const [
                Color(0xFFE0E0E0),
                Color(0xFFF5F5F5),
                Color(0xFFE0E0E0),
              ],
            ),
          ),
        );
      },
    );
  }
}


/// Price tag widget
class PriceTag extends StatelessWidget {
  final double price;
  final double? originalPrice;
  final String currency;

  const PriceTag({
    super.key,
    required this.price,
    this.originalPrice,
    this.currency = '\$',
  });

  @override
  Widget build(BuildContext context) {
    final hasDiscount = originalPrice != null && originalPrice! > price;
    
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          '$currency${price.toStringAsFixed(2)}',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: AppTheme.primaryColor,
          ),
        ),
        if (hasDiscount) ...[
          const SizedBox(width: 8),
          Text(
            '$currency${originalPrice!.toStringAsFixed(2)}',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey,
              decoration: TextDecoration.lineThrough,
            ),
          ),
        ],
      ],
    );
  }
}


/// Order status timeline widget
class OrderTimeline extends StatelessWidget {
  final String currentStatus;

  const OrderTimeline({super.key, required this.currentStatus});

  static const statuses = ['pending', 'accepted', 'preparing', 'ready', 'out_for_delivery', 'delivered'];
  static const statusLabels = {
    'pending': '📋 Order Placed',
    'accepted': '✅ Confirmed',
    'preparing': '👨‍🍳 Preparing',
    'ready': '📦 Ready',
    'out_for_delivery': '🚗 On the Way',
    'delivered': '🎉 Delivered',
  };

  @override
  Widget build(BuildContext context) {
    final currentIndex = statuses.indexOf(currentStatus);
    
    return Column(
      children: List.generate(statuses.length, (index) {
        final isActive = index <= currentIndex;
        final isCurrent = index == currentIndex;
        final status = statuses[index];
        
        return Row(
          children: [
            Column(
              children: [
                Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    color: isActive ? AppTheme.primaryColor : Colors.grey[300],
                    shape: BoxShape.circle,
                  ),
                  child: isActive
                      ? const Icon(Icons.check, size: 18, color: Colors.white)
                      : null,
                ),
                if (index < statuses.length - 1)
                  Container(
                    width: 2,
                    height: 30,
                    color: isActive && index < currentIndex
                        ? AppTheme.primaryColor
                        : Colors.grey[300],
                  ),
              ],
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Text(
                  statusLabels[status] ?? status,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                    color: isActive ? Colors.black : Colors.grey,
                  ),
                ),
              ),
            ),
          ],
        );
      }),
    );
  }
}


/// Quantity selector widget
class QuantitySelector extends StatelessWidget {
  final int quantity;
  final ValueChanged<int> onChanged;
  final int min;
  final int max;

  const QuantitySelector({
    super.key,
    required this.quantity,
    required this.onChanged,
    this.min = 1,
    this.max = 99,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(25),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(
            icon: const Icon(Icons.remove),
            onPressed: quantity > min ? () => onChanged(quantity - 1) : null,
            iconSize: 20,
          ),
          SizedBox(
            width: 32,
            child: Text(
              '$quantity',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: quantity < max ? () => onChanged(quantity + 1) : null,
            iconSize: 20,
            color: AppTheme.primaryColor,
          ),
        ],
      ),
    );
  }
}


/// Coupon input field
class CouponField extends StatefulWidget {
  final Function(String) onApply;
  final bool isLoading;

  const CouponField({
    super.key,
    required this.onApply,
    this.isLoading = false,
  });

  @override
  State<CouponField> createState() => _CouponFieldState();
}

class _CouponFieldState extends State<CouponField> {
  final _controller = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[300]!),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          const Icon(Icons.local_offer, color: AppTheme.primaryColor),
          const SizedBox(width: 8),
          Expanded(
            child: TextField(
              controller: _controller,
              decoration: const InputDecoration(
                hintText: 'Enter coupon code',
                border: InputBorder.none,
              ),
              textCapitalization: TextCapitalization.characters,
            ),
          ),
          TextButton(
            onPressed: widget.isLoading
                ? null
                : () => widget.onApply(_controller.text),
            child: widget.isLoading
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Apply'),
          ),
        ],
      ),
    );
  }
}
