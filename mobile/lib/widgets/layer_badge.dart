import 'package:flutter/material.dart';

class LayerBadge extends StatelessWidget {
  final String layerName;

  const LayerBadge({super.key, required this.layerName});

  @override
  Widget build(BuildContext context) {
    IconData icon;
    Color accentColor;

    if (layerName.contains('Rules')) {
      icon = Icons.security_rounded;
      accentColor = const Color(0xFF38BDF8); // Cyan
    } else if (layerName.contains('ML') || layerName.contains('Classifier')) {
      icon = Icons.psychology_rounded;
      accentColor = const Color(0xFFA855F7); // Purple
    } else if (layerName.contains('Groq') || layerName.contains('LLM')) {
      icon = Icons.auto_awesome_rounded;
      accentColor = const Color(0xFFF59E0B); // Amber
    } else {
      icon = Icons.check_circle_outline_rounded;
      accentColor = const Color(0xFF10B981); // Emerald
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: accentColor.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: accentColor.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: accentColor),
          const SizedBox(width: 6),
          Text(
            layerName,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: accentColor,
            ),
          ),
        ],
      ),
    );
  }
}
