import 'package:flutter/material.dart';
import '../models/scan_result.dart';
import '../services/api_service.dart';
import '../services/history_service.dart';
import '../theme/app_theme.dart';
import '../widgets/message_card.dart';
import 'feedback_dialog.dart';

class BatchScreen extends StatefulWidget {
  final ApiService apiService;

  const BatchScreen({super.key, required this.apiService});

  @override
  State<BatchScreen> createState() => _BatchScreenState();
}

class _BatchScreenState extends State<BatchScreen> {
  bool _isLoading = false;
  BatchScanSummary? _summary;
  String _activeFilter = 'ALL';

  final List<Map<String, String>> _sampleInbox = [
    {
      'sender_id': 'VM-HDFCBK',
      'text': 'Dear Customer, your NetBanking access is locked due to unverified KYC. Click http://192.168.0.12/hdfc-kyc to update immediately.',
    },
    {
      'sender_id': 'AX-SWIGGY',
      'text': 'Your Swiggy order from Biryani Blues is arriving in 15 mins. Track your rider on app.',
    },
    {
      'sender_id': '+919988776655',
      'text': 'Electricity Alert: Power will be disconnected tonight at 9:30 PM for unpaid bill. Call 9876543210 immediately to pay.',
    },
    {
      'sender_id': 'VK-SBINB',
      'text': 'Dear Customer, INR 3,500.00 debited from A/c XX8921 on 15-Oct-26. Avail Bal: INR 28,140.00. If not you, call 1800112211.',
    },
    {
      'sender_id': '+918888888888',
      'text': 'You have won Rs 50,000 cash reward in lucky draw! Pay 499 processing fee via UPI to claim prize now: upi://pay?pa=scam@upi',
    },
    {
      'sender_id': '+919123456789',
      'text': 'Hey Rahul, let us catch up this weekend for coffee!',
    },
    {
      'sender_id': '+917777777777',
      'text': 'Part-time job: Earn Rs 4,000 daily from home by liking videos. Contact HR on Telegram @scamjob',
    },
    {
      'sender_id': 'AX-ZEPTO',
      'text': 'Your Zepto groceries order #ZP-9812 has been delivered. Enjoy 10-min delivery!',
    },
  ];

  @override
  void initState() {
    super.initState();
    _scanInbox();
  }

  Future<void> _scanInbox() async {
    setState(() => _isLoading = true);

    final summary = await widget.apiService.scanBatch(_sampleInbox);
    HistoryService().addAll(summary.results);

    if (mounted) {
      setState(() {
        _summary = summary;
        _isLoading = false;
      });
    }
  }

  void _showDetailSheet(ScanResult result) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        final color = AppTheme.getVerdictColor(result.label);
        final theme = Theme.of(ctx);

        return Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: theme.cardTheme.color ?? theme.scaffoldBackgroundColor,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.withValues(alpha: 0.3),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    result.senderId.isNotEmpty ? result.senderId : 'Unknown Sender',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: color.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: color.withValues(alpha: 0.4)),
                    ),
                    child: Text(
                      result.label,
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: color,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  result.text,
                  style: const TextStyle(fontSize: 14, height: 1.4),
                ),
              ),
              const SizedBox(height: 16),
              const Text('Reasons & Indicators:', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              ...result.reasons.map((r) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(Icons.check_circle_outline, size: 14, color: color),
                        const SizedBox(width: 8),
                        Expanded(child: Text(r, style: const TextStyle(fontSize: 13))),
                      ],
                    ),
                  )),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () {
                    Navigator.pop(ctx);
                    FeedbackDialog.show(
                      context,
                      text: result.text,
                      predictedLabel: result.label,
                      apiService: widget.apiService,
                    );
                  },
                  icon: const Icon(Icons.feedback_outlined, size: 16),
                  label: const Text('Report Incorrect Verdict'),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    List<ScanResult> filteredList = [];
    if (_summary != null) {
      if (_activeFilter == 'ALL') {
        filteredList = _summary!.results;
      } else {
        filteredList = _summary!.results.where((r) => r.label == _activeFilter).toList();
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Inbox Batch Scan'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: _isLoading ? null : _scanInbox,
            tooltip: 'Re-scan inbox',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Scanning simulated inbox messages...'),
                ],
              ),
            )
          : Column(
              children: [
                // Top KPI Summary Cards
                if (_summary != null)
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: [
                        _buildKpiCard('Total', '${_summary!.total}', Colors.blue),
                        const SizedBox(width: 8),
                        _buildKpiCard('Spam', '${_summary!.spamCount}', AppTheme.spamRed),
                        const SizedBox(width: 8),
                        _buildKpiCard('Suspicious', '${_summary!.suspiciousCount}', AppTheme.suspiciousAmber),
                        const SizedBox(width: 8),
                        _buildKpiCard('Safe', '${_summary!.safeCount}', AppTheme.safeGreen),
                      ],
                    ),
                  ),

                // Filter Tabs
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Row(
                    children: [
                      _buildFilterChip('ALL', 'All (${_summary?.total ?? 0})'),
                      const SizedBox(width: 6),
                      _buildFilterChip('SPAM', 'Spam (${_summary?.spamCount ?? 0})'),
                      const SizedBox(width: 6),
                      _buildFilterChip('SUSPICIOUS', 'Suspicious (${_summary?.suspiciousCount ?? 0})'),
                      const SizedBox(width: 6),
                      _buildFilterChip('SAFE', 'Safe (${_summary?.safeCount ?? 0})'),
                    ],
                  ),
                ),
                const SizedBox(height: 12),

                // Message List
                Expanded(
                  child: filteredList.isEmpty
                      ? const Center(child: Text('No messages in this category.'))
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: filteredList.length,
                          itemBuilder: (context, i) {
                            final res = filteredList[i];
                            return MessageCard(
                              result: res,
                              onTap: () => _showDetailSheet(res),
                            );
                          },
                        ),
                ),
              ],
            ),
    );
  }

  Widget _buildKpiCard(String label, String value, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Column(
          children: [
            Text(
              value,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: color.withValues(alpha: 0.8),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilterChip(String filterKey, String label) {
    final isSelected = _activeFilter == filterKey;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _activeFilter = filterKey),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 6),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: isSelected ? AppTheme.accentCyan : Colors.transparent,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: isSelected ? AppTheme.accentCyan : Colors.grey.withValues(alpha: 0.3),
            ),
          ),
          child: Text(
            label,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: isSelected ? Colors.white : Colors.grey,
            ),
          ),
        ),
      ),
    );
  }
}
