import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/scan_result.dart';
import '../services/api_service.dart';
import '../services/history_service.dart';
import '../theme/app_theme.dart';
import '../widgets/risk_meter.dart';
import '../widgets/layer_badge.dart';
import 'feedback_dialog.dart';

class ScanScreen extends StatefulWidget {
  final ApiService apiService;

  const ScanScreen({super.key, required this.apiService});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final TextEditingController _textCtrl = TextEditingController();
  final TextEditingController _senderCtrl = TextEditingController();
  bool _isLoading = false;
  ScanResult? _currentResult;
  bool _serverOnline = false;

  final List<Map<String, String>> _samplePresets = [
    {
      'title': '🚨 Bank KYC Scam',
      'text': 'Your SBI account has been blocked due to pending KYC. Update immediately at http://192.168.1.10/sbi-kyc to avoid permanent suspension.',
      'sender': '+919876543210',
    },
    {
      'title': '⚡ Electricity Scam',
      'text': 'Dear consumer, your electricity connection will be cut off tonight at 9:30 PM due to unpaid bill. Call 9876543210 immediately.',
      'sender': '+919988776655',
    },
    {
      'title': '✅ Genuine Debit Alert',
      'text': 'Dear SBI Customer, INR 5,000.00 debited from A/c XX1234 on 15-Oct-26 at 10:15:30. Avail Bal: INR 42,350.00. Call 1800112211 if not you.',
      'sender': 'VM-SBINB',
    },
    {
      'title': '🔑 Food Delivery OTP',
      'text': 'Your Swiggy verification code is 492810. Valid for 10 minutes. Do not share this OTP with anyone.',
      'sender': 'AX-SWIGGY',
    },
    {
      'title': '🎁 UPI Lottery Fraud',
      'text': 'Congratulations! You won Rs 50,000 lottery cash prize in PhonePe Diwali spin! Pay processing fee Rs 499 via UPI to claim immediately: upi://pay?pa=scam@upi',
      'sender': '+918888888888',
    },
    {
      'title': '💼 Part-Time Job Scam',
      'text': 'Work from home part-time and earn Rs 3,000 to Rs 8,000 daily by simply subscribing to YouTube videos. Contact HR on Telegram @scamjob now.',
      'sender': '+917777777777',
    },
  ];

  @override
  void initState() {
    super.initState();
    _checkServer();
  }

  @override
  void dispose() {
    _textCtrl.dispose();
    _senderCtrl.dispose();
    super.dispose();
  }

  Future<void> _checkServer() async {
    final online = await widget.apiService.checkHealth();
    if (mounted) setState(() => _serverOnline = online);
  }

  Future<void> _pasteClipboard() async {
    final data = await Clipboard.getData('text/plain');
    if (data?.text != null && data!.text!.isNotEmpty) {
      setState(() {
        _textCtrl.text = data.text!;
      });
    }
  }

  Future<void> _runScan() async {
    final text = _textCtrl.text.trim();
    if (text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter or paste a message to scan.'),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    setState(() => _isLoading = true);

    final result = await widget.apiService.scanMessage(
      text,
      senderId: _senderCtrl.text.trim(),
    );

    HistoryService().add(result);

    if (mounted) {
      setState(() {
        _currentResult = result;
        _isLoading = false;
      });
    }
  }

  void _loadPreset(Map<String, String> preset) {
    setState(() {
      _textCtrl.text = preset['text']!;
      _senderCtrl.text = preset['sender']!;
      _currentResult = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(7),
              decoration: BoxDecoration(
                color: AppTheme.accentCyan.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.shield_rounded, color: AppTheme.accentCyan, size: 22),
            ),
            const SizedBox(width: 10),
            const Text('Spam Shield'),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: _serverOnline
                  ? AppTheme.safeGreen.withValues(alpha: 0.15)
                  : Colors.orange.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: _serverOnline ? AppTheme.safeGreen : Colors.orange,
                width: 0.8,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 7,
                  height: 7,
                  decoration: BoxDecoration(
                    color: _serverOnline ? AppTheme.safeGreen : Colors.orange,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                Text(
                  _serverOnline ? 'Backend API' : 'Local Engine',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: _serverOnline ? AppTheme.safeGreen : Colors.orange,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Quick Presets Carousel
            SizedBox(
              height: 38,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: _samplePresets.length,
                separatorBuilder: (_, __) => const SizedBox(width: 8),
                itemBuilder: (context, i) {
                  final preset = _samplePresets[i];
                  return ActionChip(
                    label: Text(
                      preset['title']!,
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                    ),
                    onPressed: () => _loadPreset(preset),
                    backgroundColor: theme.cardTheme.color,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20),
                      side: BorderSide(color: Colors.grey.withValues(alpha: 0.2)),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 16),

            // Message Input Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Message Text',
                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
                        ),
                        Row(
                          children: [
                            TextButton.icon(
                              onPressed: _pasteClipboard,
                              icon: const Icon(Icons.content_paste_rounded, size: 16),
                              label: const Text('Paste', style: TextStyle(fontSize: 12)),
                              style: TextButton.styleFrom(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                visualDensity: VisualDensity.compact,
                              ),
                            ),
                            if (_textCtrl.text.isNotEmpty)
                              IconButton(
                                icon: const Icon(Icons.clear_rounded, size: 18),
                                onPressed: () => setState(() {
                                  _textCtrl.clear();
                                  _currentResult = null;
                                }),
                                visualDensity: VisualDensity.compact,
                              ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _textCtrl,
                      maxLines: 5,
                      minLines: 3,
                      decoration: const InputDecoration(
                        hintText: 'Paste SMS, WhatsApp, or Telegram short message here...',
                      ),
                      onChanged: (_) {
                        if (_currentResult != null) setState(() => _currentResult = null);
                      },
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _senderCtrl,
                      decoration: const InputDecoration(
                        labelText: 'Sender Header / Phone (Optional)',
                        hintText: 'e.g. AX-HDFCBK, VM-SBINB, or +919876543210',
                        prefixIcon: Icon(Icons.perm_phone_msg_rounded, size: 18),
                        isDense: true,
                      ),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: _isLoading ? null : _runScan,
                      icon: _isLoading
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                            )
                          : const Icon(Icons.radar_rounded),
                      label: Text(_isLoading ? 'Analyzing Multi-Layer Defense...' : 'Scan Message'),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Scan Result Card
            if (_currentResult != null) ...[
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      // Risk Meter
                      RiskMeter(
                        riskScore: _currentResult!.riskScore,
                        label: _currentResult!.label,
                        confidence: _currentResult!.confidence,
                      ),
                      const SizedBox(height: 16),

                      // Latency & Layers Badge
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.bolt_rounded, size: 15, color: Colors.amber.shade600),
                          const SizedBox(width: 4),
                          Text(
                            'Latency: ${_currentResult!.latencyMs.toStringAsFixed(1)} ms',
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(width: 12),
                          const Icon(Icons.layers_rounded, size: 15, color: AppTheme.accentCyan),
                          const SizedBox(width: 4),
                          Text(
                            '${_currentResult!.layersUsed.length} Layers Evaluated',
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                      const Divider(height: 32),

                      // Reasons Section
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          'Detection Insights & Reasons',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                            color: theme.textTheme.bodySmall?.color,
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      ..._currentResult!.reasons.map(
                        (reason) => Padding(
                          padding: const EdgeInsets.only(bottom: 6),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Padding(
                                padding: const EdgeInsets.only(top: 2),
                                child: Icon(
                                  _currentResult!.label == 'SAFE'
                                      ? Icons.check_circle_rounded
                                      : Icons.warning_rounded,
                                  size: 16,
                                  color: AppTheme.getVerdictColor(_currentResult!.label),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  reason,
                                  style: const TextStyle(fontSize: 13, height: 1.3),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                      // Layer Breakdown Card
                      const SizedBox(height: 12),
                      ExpansionTile(
                        tilePadding: EdgeInsets.zero,
                        title: const Text(
                          'View Deep Layer Inspection',
                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                        ),
                        children: [
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.black.withValues(alpha: 0.05),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                _buildLayerRow('Layer 1 (Rules)', 'Heuristics, lookalike URLs, IP links & context exemptions'),
                                const SizedBox(height: 8),
                                _buildLayerRow('Layer 2 (ML)', 'Logistic Regression with 28k word & char n-grams'),
                                const SizedBox(height: 8),
                                _buildLayerRow('Layer 3 (Groq LLM)', 'Invoked only when ML is ambiguous (0.35 - 0.65)'),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),

                      // Feedback Action
                      OutlinedButton.icon(
                        onPressed: () {
                          FeedbackDialog.show(
                            context,
                            text: _currentResult!.text,
                            predictedLabel: _currentResult!.label,
                            apiService: widget.apiService,
                          );
                        },
                        icon: const Icon(Icons.feedback_outlined, size: 16),
                        label: const Text('Report Incorrect Verdict'),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildLayerRow(String title, String desc) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
        const SizedBox(height: 2),
        Text(desc, style: const TextStyle(fontSize: 11, color: Colors.grey)),
      ],
    );
  }
}
