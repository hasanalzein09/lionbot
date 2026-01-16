import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';

class LoyaltyScreen extends StatefulWidget {
  const LoyaltyScreen({super.key});

  @override
  State<LoyaltyScreen> createState() => _LoyaltyScreenState();
}

class _LoyaltyScreenState extends State<LoyaltyScreen> {
  Map<String, dynamic>? _tierInfo;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final info = await ApiService().getTierInfo();
      if (mounted) setState(() { _tierInfo = info; _isLoading = false; });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Loyalty Program')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryColor))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(colors: [AppTheme.primaryColor, AppTheme.primaryColor.withOpacity(0.7)]),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.card_giftcard, size: 48, color: Colors.black),
                        SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Loyalty Program', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.black)),
                              Text('Manage tiers & rewards', style: TextStyle(color: Colors.black54)),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  // Tiers
                  const Text('Loyalty Tiers', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  ...(_tierInfo?['tiers'] as List? ?? []).map((tier) => _buildTierCard(tier)),
                ],
              ),
            ),
    );
  }

  Widget _buildTierCard(Map<String, dynamic> tier) {
    final colors = {
      'bronze': Colors.brown,
      'silver': Colors.grey,
      'gold': AppTheme.primaryColor,
      'platinum': Colors.blueGrey,
    };
    final color = colors[tier['name']] ?? AppTheme.primaryColor;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
                child: Icon(Icons.stars, color: color),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text((tier['name'] as String).toUpperCase(), style: TextStyle(fontWeight: FontWeight.bold, color: color)),
                    Text('${tier['points_required']} points required', style: TextStyle(fontSize: 12, color: Colors.white.withOpacity(0.6))),
                  ],
                ),
              ),
              Text('${tier['multiplier']}x', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
            ],
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            children: (tier['benefits'] as List? ?? []).map<Widget>((b) => Chip(
              label: Text(b, style: const TextStyle(fontSize: 11)),
              backgroundColor: AppTheme.surfaceDark,
            )).toList(),
          ),
        ],
      ),
    );
  }
}
