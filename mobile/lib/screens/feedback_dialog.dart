import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class FeedbackDialog extends StatefulWidget {
  final String text;
  final String predictedLabel;
  final ApiService apiService;

  const FeedbackDialog({
    super.key,
    required this.text,
    required this.predictedLabel,
    required this.apiService,
  });

  static Future<void> show(
    BuildContext context, {
    required String text,
    required String predictedLabel,
    required ApiService apiService,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => FeedbackDialog(
        text: text,
        predictedLabel: predictedLabel,
        apiService: apiService,
      ),
    );
  }

  @override
  State<FeedbackDialog> createState() => _FeedbackDialogState();
}

class _FeedbackDialogState extends State<FeedbackDialog> {
  late String _selectedCorrection;
  final TextEditingController _commentCtrl = TextEditingController();
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    // Default suggestion opposite of prediction
    if (widget.predictedLabel == 'SPAM') {
      _selectedCorrection = 'SAFE';
    } else {
      _selectedCorrection = 'SPAM';
    }
  }

  @override
  void dispose() {
    _commentCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() => _isSubmitting = true);
    final success = await widget.apiService.sendFeedback(
      text: widget.text,
      predictedLabel: widget.predictedLabel,
      userCorrection: _selectedCorrection,
      comments: _commentCtrl.text.trim(),
    );
    if (!mounted) return;
    setState(() => _isSubmitting = false);

    Navigator.pop(context);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          success
              ? 'Thank you! Your feedback helps retrain and improve Spam Shield.'
              : 'Feedback recorded locally.',
        ),
        backgroundColor: AppTheme.safeGreenDark,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;
    final theme = Theme.of(context);

    return Container(
      padding: EdgeInsets.only(
        top: 20,
        left: 20,
        right: 20,
        bottom: bottomInset + 20,
      ),
      decoration: BoxDecoration(
        color: theme.cardTheme.color ?? theme.scaffoldBackgroundColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: SingleChildScrollView(
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
            const Text(
              'Report Message or Classification',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 6),
            Text(
              'Help us fine-tune our detection models. What should this message be marked as?',
              style: TextStyle(
                fontSize: 13,
                color: theme.textTheme.bodySmall?.color,
              ),
            ),
            const SizedBox(height: 16),

            // Radio choices
            RadioListTile<String>(
              title: const Text('It is SPAM / Scam (Phishing, fraud, fake job/lottery)'),
              value: 'SPAM',
              groupValue: _selectedCorrection,
              activeColor: AppTheme.spamRed,
              onChanged: (val) => setState(() => _selectedCorrection = val!),
            ),
            RadioListTile<String>(
              title: const Text('It is SUSPICIOUS (Unsolicited promotion or unverified link)'),
              value: 'SUSPICIOUS',
              groupValue: _selectedCorrection,
              activeColor: AppTheme.suspiciousAmber,
              onChanged: (val) => setState(() => _selectedCorrection = val!),
            ),
            RadioListTile<String>(
              title: const Text('It is SAFE (Legitimate transactional alert, OTP, or friend)'),
              value: 'SAFE',
              groupValue: _selectedCorrection,
              activeColor: AppTheme.safeGreen,
              onChanged: (val) => setState(() => _selectedCorrection = val!),
            ),
            const SizedBox(height: 12),

            // Comment text input
            TextField(
              controller: _commentCtrl,
              maxLines: 2,
              decoration: const InputDecoration(
                hintText: 'Additional details (optional, e.g. "Known electricity scam")',
              ),
            ),
            const SizedBox(height: 20),

            // Action buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Cancel'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _isSubmitting ? null : _submit,
                    child: _isSubmitting
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          )
                        : const Text('Submit Feedback'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
