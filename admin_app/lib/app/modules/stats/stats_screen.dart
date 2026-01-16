import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/api_service.dart';

class StatsScreen extends StatefulWidget {
  const StatsScreen({super.key});

  @override
  State<StatsScreen> createState() => _StatsScreenState();
}

class _StatsScreenState extends State<StatsScreen> {
  Map<String, dynamic>? _stats;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    try {
      final stats = await ApiService().getDashboardStats();
      if (mounted) setState(() { _stats = stats; _isLoading = false; });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Analytics')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryColor))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Revenue Chart
                  const Text('Revenue Overview', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                  const SizedBox(height: 16),
                  Container(
                    height: 200,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(color: AppTheme.cardDark, borderRadius: BorderRadius.circular(16)),
                    child: LineChart(
                      LineChartData(
                        gridData: const FlGridData(show: false),
                        titlesData: const FlTitlesData(show: false),
                        borderData: FlBorderData(show: false),
                        lineBarsData: [
                          LineChartBarData(
                            spots: [
                              const FlSpot(0, 3), const FlSpot(1, 4), const FlSpot(2, 3.5),
                              const FlSpot(3, 5), const FlSpot(4, 4), const FlSpot(5, 6), const FlSpot(6, 5.5),
                            ],
                            isCurved: true,
                            color: AppTheme.primaryColor,
                            barWidth: 3,
                            dotData: const FlDotData(show: false),
                            belowBarData: BarAreaData(
                              show: true,
                              color: AppTheme.primaryColor.withOpacity(0.1),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Order Stats
                  const Text('Order Statistics', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(child: _buildStatBox('Total', '${_stats?['total_orders'] ?? 0}', AppTheme.primaryColor)),
                      const SizedBox(width: 12),
                      Expanded(child: _buildStatBox('Pending', '${_stats?['pending_orders'] ?? 0}', AppTheme.warningColor)),
                      const SizedBox(width: 12),
                      Expanded(child: _buildStatBox('Delivered', '${_stats?['delivered_orders'] ?? 0}', AppTheme.accentColor)),
                    ],
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Order Status Pie
                  const Text('Order Distribution', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                  const SizedBox(height: 16),
                  Container(
                    height: 200,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(color: AppTheme.cardDark, borderRadius: BorderRadius.circular(16)),
                    child: PieChart(
                      PieChartData(
                        sectionsSpace: 2,
                        centerSpaceRadius: 40,
                        sections: [
                          PieChartSectionData(value: 35, color: AppTheme.accentColor, title: '35%', titleStyle: const TextStyle(fontSize: 12, color: Colors.white)),
                          PieChartSectionData(value: 25, color: AppTheme.primaryColor, title: '25%', titleStyle: const TextStyle(fontSize: 12, color: Colors.white)),
                          PieChartSectionData(value: 20, color: Colors.blueAccent, title: '20%', titleStyle: const TextStyle(fontSize: 12, color: Colors.white)),
                          PieChartSectionData(value: 20, color: AppTheme.warningColor, title: '20%', titleStyle: const TextStyle(fontSize: 12, color: Colors.white)),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Legend
                  Wrap(
                    spacing: 16,
                    children: [
                      _buildLegendItem('Delivered', AppTheme.accentColor),
                      _buildLegendItem('In Transit', AppTheme.primaryColor),
                      _buildLegendItem('Preparing', Colors.blueAccent),
                      _buildLegendItem('Pending', AppTheme.warningColor),
                    ],
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildStatBox(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
      child: Column(
        children: [
          Text(value, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: color)),
          const SizedBox(height: 4),
          Text(label, style: TextStyle(fontSize: 12, color: Colors.white.withOpacity(0.6))),
        ],
      ),
    );
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(width: 12, height: 12, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
