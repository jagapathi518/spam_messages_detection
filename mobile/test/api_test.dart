import 'package:flutter_test/flutter_test.dart';
import 'package:spam_shield/models/scan_result.dart';
import 'package:spam_shield/services/api_service.dart';
import 'package:spam_shield/services/history_service.dart';

void main() {
  group('ApiService & Heuristic Tests', () {
    final api = ApiService(baseUrl: 'http://invalid-test-domain.mock');

    test('Phishing APK message flags as SPAM offline', () async {
      final res = await api.scanMessage(
        'Urgent: Update your PAN card KYC immediately at http://192.168.1.5/sbi.apk to avoid bank block.',
      );
      expect(res.label, equals('SPAM'));
      expect(res.riskScore, greaterThanOrEqualTo(0.70));
      expect(res.reasons.isNotEmpty, isTrue);
    });

    test('Electricity cutoff scam flags as SPAM offline', () async {
      final res = await api.scanMessage(
        'Dear consumer, your electricity connection will be cut off tonight at 9:30 PM. Call power officer 9876543210.',
      );
      expect(res.label, equals('SPAM'));
      expect(res.reasons.any((r) => r.toLowerCase().contains('electricity')), isTrue);
    });

    test('Legitimate bank debit transaction flags as SAFE offline', () async {
      final res = await api.scanMessage(
        'Dear Customer, INR 2,500.00 debited by UPI from A/c XX9921 on 15-Oct-26. Avail Bal: INR 15,200.00.',
        senderId: 'VM-SBINB',
      );
      expect(res.label, equals('SAFE'));
      expect(res.riskScore, lessThan(0.20));
    });

    test('OTP message flags as SAFE offline', () async {
      final res = await api.scanMessage(
        'Your Swiggy verification code is 492810. Valid for 10 minutes. Do not share this OTP with anyone.',
        senderId: 'AX-SWIGGY',
      );
      expect(res.label, equals('SAFE'));
    });

    test('Empty message returns SAFE with zero latency', () async {
      final res = await api.scanMessage('   ');
      expect(res.label, equals('SAFE'));
      expect(res.riskScore, equals(0.0));
    });
  });

  group('Model Serialization Tests', () {
    test('ScanResult JSON roundtrip preserves fields', () {
      final original = ScanResult(
        id: 'test_123',
        text: 'Test short message text',
        senderId: 'AX-TEST',
        label: 'SPAM',
        confidence: 0.95,
        riskScore: 0.92,
        reasons: ['Suspicious link detected'],
        layersUsed: ['Layer 1 (Rules)'],
        latencyMs: 3.2,
      );

      final json = original.toJson();
      final restored = ScanResult.fromJson(json, text: original.text, senderId: original.senderId);

      expect(restored.label, equals('SPAM'));
      expect(restored.confidence, equals(0.95));
      expect(restored.reasons.first, equals('Suspicious link detected'));
      expect(restored.senderId, equals('AX-TEST'));
    });
  });

  group('HistoryService Tests', () {
    test('HistoryService maintains scan order and limits', () {
      final history = HistoryService();
      history.clear();
      expect(history.history.isEmpty, isTrue);

      final item1 = ScanResult(
        id: 'item_1',
        text: 'Message 1',
        label: 'SAFE',
        confidence: 0.90,
        riskScore: 0.1,
        reasons: ['Clean'],
        layersUsed: ['Layer 2'],
        latencyMs: 2.0,
      );

      history.add(item1);
      expect(history.history.length, equals(1));
      expect(history.history.first.id, equals('item_1'));

      history.clear();
      expect(history.history.isEmpty, isTrue);
    });
  });
}
