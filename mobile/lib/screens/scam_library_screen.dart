import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class ScamLibraryScreen extends StatelessWidget {
  const ScamLibraryScreen({super.key});

  static const List<Map<String, dynamic>> _scams = [
    {
      'title': 'Bank KYC / Account Deactivation Scam',
      'category': 'Financial Credential Harvesting',
      'icon': Icons.account_balance_rounded,
      'color': AppTheme.spamRed,
      'riskLevel': 'CRITICAL',
      'threat': 'Threatens immediate bank account suspension or debit card block due to pending KYC.',
      'mechanism': 'Victims are directed to a phishing replica of NetBanking or instructed to install a malicious APK file that intercepts 2FA OTP SMS.',
      'example': 'Dear SBI Customer, your YONO account is blocked today due to pending PAN KYC. Update immediately at http://192.168.1.10/sbi-verify.apk to avoid suspension.',
      'countermeasure': 'Banks never ask for KYC updates over SMS links. Genuine bank SMS arrive with 6-character alphanumeric headers (e.g., VM-SBINB, AX-HDFCBK), never 10-digit mobile numbers.',
    },
    {
      'title': 'Electricity / Power Cutoff Scam',
      'category': 'Urgency & Extortion Fraud',
      'icon': Icons.bolt_rounded,
      'color': AppTheme.suspiciousAmber,
      'riskLevel': 'HIGH',
      'threat': 'Claims electricity will be disconnected tonight at 9:30 PM due to an unpaid previous month bill.',
      'mechanism': 'Victims are pressured into calling a personal mobile number. The scammer asks them to download remote-access apps (AnyDesk, QuickSupport) to pay a token Rs 10 bill, which empties their accounts.',
      'example': 'Dear consumer, your electricity connection will be cut off tonight at 9:30 PM by electricity office because your previous month bill was not updated. Immediately contact officer 9876543210.',
      'countermeasure': 'Power utility boards give 15-day statutory physical notice before disconnection. Disconnections never occur at night. Official discoms never provide personal mobile numbers.',
    },
    {
      'title': 'Traffic e-Challan APK Malware',
      'category': 'Trojan / Remote Access Trojan (RAT)',
      'icon': Icons.directions_car_rounded,
      'color': AppTheme.spamRed,
      'riskLevel': 'CRITICAL',
      'threat': 'Sends fake police traffic fine notices with links to download malicious Android APKs.',
      'mechanism': 'The APK file (e.g., Parivahan_challan.apk) requests Accessibility and SMS permissions to silently read bank OTPs and forward them to fraud command servers.',
      'example': 'Notice: Pending traffic fine of Rs 1,000 for your vehicle DL01AB1234. Pay immediately or vehicle RC will be cancelled: http://echallan-parivahan.apk',
      'countermeasure': 'Government e-challans never distribute APK files. Official traffic fines are only viewed and paid on https://echallan.parivahan.gov.in.',
    },
    {
      'title': 'UPI PIN / Lottery Advance Fee Fraud',
      'category': 'Social Engineering / Payment Fraud',
      'icon': Icons.card_giftcard_rounded,
      'color': AppTheme.spamRed,
      'riskLevel': 'HIGH',
      'threat': 'Claims you won a cash lottery (KBC, PhonePe Diwali Spin, Jio Lucky Draw).',
      'mechanism': 'The scammer sends a UPI collect request or asks the victim to enter their UPI PIN to "receive" the prize money. Entering UPI PIN transfers money OUT of your account.',
      'example': 'Congratulations! You won Rs 50,000 in lucky spin! Enter UPI PIN to claim instant cashback reward: upi://pay?pa=claim@upi',
      'countermeasure': 'GOLDEN RULE: You NEVER need to enter your UPI PIN to receive money. UPI PIN is only needed to pay or transfer money out.',
    },
    {
      'title': 'Telegram / Part-Time Job Scam',
      'category': 'Task Scam / Investment Fraud',
      'icon': Icons.work_outline_rounded,
      'color': AppTheme.suspiciousAmber,
      'riskLevel': 'HIGH',
      'threat': 'Offers Rs 3,000 to Rs 8,000 daily for easy online tasks (liking YouTube videos, reviewing hotels).',
      'mechanism': 'Victims earn small payouts initially (Rs 150), then are lured into Telegram VIP groups where they are asked to invest larger sums in "prepaid crypto tasks" that cannot be withdrawn.',
      'example': 'Earn Rs 5,000 daily from home! Part-time work for students and homemakers. Simple YouTube like tasks. Join HR on Telegram @scamjob_hr.',
      'countermeasure': 'No legitimate company hires over Telegram or pays high daily wages for simple video likes. Never deposit money to earn a salary.',
    },
    {
      'title': 'Fake Courier / Postal Address Phishing',
      'category': 'Package Phishing',
      'icon': Icons.local_shipping_outlined,
      'color': AppTheme.accentCyan,
      'riskLevel': 'MEDIUM',
      'threat': 'Claims a parcel could not be delivered due to missing house number or unpaid Rs 25 customs fee.',
      'mechanism': 'Victims click a link to a fake India Post or courier tracking site and enter credit/debit card numbers for a nominal fee, exposing card details to unauthorized recurring charges.',
      'example': 'India Post: Your package #IN-8912 could not be delivered due to incomplete street address. Please update your details within 12h: http://indiapost-update.xyz',
      'countermeasure': 'Legitimate couriers (BlueDart, Delhivery, India Post) hold parcels at local hubs and call using registered logistics numbers. They never send shortened web links for address corrections.',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scam Threat Library'),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _scams.length,
        itemBuilder: (context, i) {
          final item = _scams[i];
          final color = item['color'] as Color;

          return Card(
            margin: const EdgeInsets.only(bottom: 16),
            child: ExpansionTile(
              tilePadding: const EdgeInsets.all(16),
              childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              leading: Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: Icon(item['icon'] as IconData, color: color, size: 24),
              ),
              title: Text(
                item['title'] as String,
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
              ),
              subtitle: Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: color.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        item['riskLevel'] as String,
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: color),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        item['category'] as String,
                        style: const TextStyle(fontSize: 11, color: Colors.grey),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
              children: [
                const Divider(),
                const SizedBox(height: 8),
                _buildSection('Threat Overview', item['threat'] as String),
                const SizedBox(height: 10),
                _buildSection('How the Scam Works', item['mechanism'] as String),
                const SizedBox(height: 10),
                _buildSection('Real Message Example', item['example'] as String, isCode: true),
                const SizedBox(height: 10),
                _buildSection('Defense & Red Flags', item['countermeasure'] as String, isHighlight: true),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildSection(String title, String content, {bool isCode = false, bool isHighlight = false}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: isHighlight ? AppTheme.safeGreen : Colors.grey,
          ),
        ),
        const SizedBox(height: 4),
        Container(
          width: double.infinity,
          padding: isCode ? const EdgeInsets.all(10) : EdgeInsets.zero,
          decoration: isCode
              ? BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey.withValues(alpha: 0.2)),
                )
              : null,
          child: Text(
            content,
            style: TextStyle(
              fontSize: 13,
              height: 1.4,
              fontFamily: isCode ? 'monospace' : null,
              fontWeight: isHighlight ? FontWeight.w500 : FontWeight.normal,
            ),
          ),
        ),
      ],
    );
  }
}
