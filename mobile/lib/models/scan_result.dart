class ScanResult {
  final String id;
  final String text;
  final String senderId;
  final String label;
  final double confidence;
  final double riskScore;
  final List<String> reasons;
  final List<String> layersUsed;
  final double latencyMs;
  final Map<String, dynamic>? layerBreakdown;
  final DateTime timestamp;

  ScanResult({
    required this.id,
    required this.text,
    this.senderId = '',
    required this.label,
    required this.confidence,
    required this.riskScore,
    required this.reasons,
    required this.layersUsed,
    required this.latencyMs,
    this.layerBreakdown,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  factory ScanResult.fromJson(
    Map<String, dynamic> json, {
    String text = '',
    String senderId = '',
    String? id,
  }) {
    return ScanResult(
      id: id ?? DateTime.now().millisecondsSinceEpoch.toString(),
      text: text.isNotEmpty ? text : (json['text_preview'] ?? ''),
      senderId: senderId,
      label: (json['label'] ?? 'SAFE').toString().toUpperCase(),
      confidence: (json['confidence'] is num) ? (json['confidence'] as num).toDouble() : 0.0,
      riskScore: (json['risk_score'] is num) ? (json['risk_score'] as num).toDouble() : 0.0,
      reasons: (json['reasons'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      layersUsed: (json['layers_used'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      latencyMs: (json['latency_ms'] is num) ? (json['latency_ms'] as num).toDouble() : 0.0,
      layerBreakdown: json['layer_breakdown'] as Map<String, dynamic>?,
      timestamp: json['created_at'] != null ? DateTime.tryParse(json['created_at']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'text': text,
      'sender_id': senderId,
      'label': label,
      'confidence': confidence,
      'risk_score': riskScore,
      'reasons': reasons,
      'layers_used': layersUsed,
      'latency_ms': latencyMs,
      'layer_breakdown': layerBreakdown,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

class BatchScanSummary {
  final int total;
  final int spamCount;
  final int suspiciousCount;
  final int safeCount;
  final double totalLatencyMs;
  final List<ScanResult> results;

  BatchScanSummary({
    required this.total,
    required this.spamCount,
    required this.suspiciousCount,
    required this.safeCount,
    required this.totalLatencyMs,
    required this.results,
  });

  factory BatchScanSummary.fromJson(
    Map<String, dynamic> json,
    List<Map<String, String>> originalMessages,
  ) {
    final rawResults = (json['results'] as List<dynamic>?) ?? [];
    final List<ScanResult> parsed = [];

    for (int i = 0; i < rawResults.length; i++) {
      final orig = i < originalMessages.length ? originalMessages[i] : null;
      parsed.add(
        ScanResult.fromJson(
          rawResults[i] as Map<String, dynamic>,
          text: orig?['text'] ?? '',
          senderId: orig?['sender_id'] ?? '',
        ),
      );
    }

    return BatchScanSummary(
      total: json['total'] ?? parsed.length,
      spamCount: json['spam_count'] ?? 0,
      suspiciousCount: json['suspicious_count'] ?? 0,
      safeCount: json['safe_count'] ?? 0,
      totalLatencyMs: (json['total_latency_ms'] is num)
          ? (json['total_latency_ms'] as num).toDouble()
          : 0.0,
      results: parsed,
    );
  }
}
