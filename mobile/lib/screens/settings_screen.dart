import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class SettingsScreen extends StatefulWidget {
  final ApiService apiService;
  final ThemeMode currentThemeMode;
  final ValueChanged<ThemeMode> onThemeChanged;

  const SettingsScreen({
    super.key,
    required this.apiService,
    required this.currentThemeMode,
    required this.onThemeChanged,
  });

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _urlCtrl;
  bool _isTesting = false;
  String? _testMessage;
  bool _testSuccess = false;
  Map<String, dynamic>? _telemetry;

  @override
  void initState() {
    super.initState();
    _urlCtrl = TextEditingController(text: widget.apiService.baseUrl);
    _loadTelemetry();
  }

  @override
  void dispose() {
    _urlCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadTelemetry() async {
    final stats = await widget.apiService.fetchStats();
    if (mounted) setState(() => _telemetry = stats);
  }

  Future<void> _testConnection() async {
    setState(() {
      _isTesting = true;
      _testMessage = null;
    });

    widget.apiService.baseUrl = _urlCtrl.text.trim();
    final healthy = await widget.apiService.checkHealth();

    if (mounted) {
      setState(() {
        _isTesting = false;
        _testSuccess = healthy;
        _testMessage = healthy
            ? 'Connected successfully to Spam Shield FastAPI Backend!'
            : 'Could not connect. Using smart local client heuristics.';
      });
      if (healthy) _loadTelemetry();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings & Architecture'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Section: Backend Configuration
          const Text(
            'BACKEND CONNECTION',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey),
          ),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TextField(
                    controller: _urlCtrl,
                    decoration: const InputDecoration(
                      labelText: 'API Base URL',
                      hintText: 'http://10.0.2.2:8000 or http://127.0.0.1:8000',
                      prefixIcon: Icon(Icons.cloud_outlined, size: 20),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            setState(() {
                              _urlCtrl.text = 'http://10.0.2.2:8000';
                            });
                          },
                          child: const Text('Android (10.0.2.2)', style: TextStyle(fontSize: 11)),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            setState(() {
                              _urlCtrl.text = 'http://127.0.0.1:8000';
                            });
                          },
                          child: const Text('Localhost (Web/Desktop)', style: TextStyle(fontSize: 11)),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton.icon(
                    onPressed: _isTesting ? null : _testConnection,
                    icon: _isTesting
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          )
                        : const Icon(Icons.sync_rounded, size: 18),
                    label: const Text('Test & Save Endpoint'),
                  ),
                  if (_testMessage != null) ...[
                    const SizedBox(height: 12),
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: _testSuccess
                            ? AppTheme.safeGreen.withValues(alpha: 0.15)
                            : Colors.orange.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        _testMessage!,
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: _testSuccess ? AppTheme.safeGreen : Colors.orange,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Section: Appearance
          const Text(
            'APPEARANCE & THEME',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey),
          ),
          const SizedBox(height: 8),
          Card(
            child: Column(
              children: [
                RadioListTile<ThemeMode>(
                  title: const Text('System Default'),
                  subtitle: const Text('Follow device theme settings'),
                  value: ThemeMode.system,
                  groupValue: widget.currentThemeMode,
                  onChanged: (mode) => widget.onThemeChanged(mode!),
                ),
                RadioListTile<ThemeMode>(
                  title: const Text('Dark Mode'),
                  subtitle: const Text('Sleek dark aesthetics for telecom cyber defense'),
                  value: ThemeMode.dark,
                  groupValue: widget.currentThemeMode,
                  onChanged: (mode) => widget.onThemeChanged(mode!),
                ),
                RadioListTile<ThemeMode>(
                  title: const Text('Light Mode'),
                  subtitle: const Text('Clean high-contrast daytime view'),
                  value: ThemeMode.light,
                  groupValue: widget.currentThemeMode,
                  onChanged: (mode) => widget.onThemeChanged(mode!),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Section: Telemetry & Cloud Stats
          if (_telemetry != null) ...[
            const Text(
              'LIVE SYSTEM TELEMETRY',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey),
            ),
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    _buildStatRow('Total Scans Processed', '${_telemetry!['total_scans']}'),
                    _buildStatRow('Spam Interceptions', '${_telemetry!['spam_detected']}'),
                    _buildStatRow('Clean Transactions Verified', '${_telemetry!['safe_verified']}'),
                    _buildStatRow('Average Latency', '${_telemetry!['avg_latency_ms']} ms'),
                    _buildStatRow('Storage Mode', '${_telemetry!['storage']}'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
          ],

          // Section: Project Architecture
          const Text(
            'ABOUT SPAM SHIELD',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey),
          ),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Spam Shield v1.0.0',
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'A specialized 3-layer security system designed EXCLUSIVELY for SHORT mobile text messages (SMS, WhatsApp, Telegram chats: bank, OTP, UPI, KYC, electricity, challan, courier scams). Emails are strictly out of scope.',
                    style: TextStyle(fontSize: 13, height: 1.4, color: Colors.grey),
                  ),
                  const Divider(height: 24),
                  const Text('Defense Architecture:', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  _buildArchBullet('Layer 1 (Rules)', 'Instant heuristics, IP links, lookalikes, obfuscation decoder & strict transactional exemptions.'),
                  _buildArchBullet('Layer 2 (ML)', 'Calibrated Logistic Regression with 28k word & character n-grams (<2.2ms latency).'),
                  _buildArchBullet('Layer 3 (Groq LLM)', 'Dynamic AI arbitration invoked only on ambiguous predictions (0.35 - 0.65) with daily rate limits.'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 13, color: Colors.grey)),
          Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildArchBullet(String title, String desc) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.shield_outlined, size: 14, color: AppTheme.accentCyan),
          const SizedBox(width: 8),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: const TextStyle(fontSize: 12, height: 1.3, color: Colors.grey),
                children: [
                  TextSpan(text: '$title: ', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                  TextSpan(text: desc),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
