"""Detection Arbiter: Coordinates Layer 1 (Rules), Layer 2 (ML), and Layer 3 (LLM).

Provides unified classification output:
{
    "label": "SPAM" | "SUSPICIOUS" | "SAFE",
    "confidence": float,
    "risk_score": float,
    "reasons": List[str],
    "layers_used": List[str]
}
"""
from typing import Dict, Any, List, Optional
from backend.app.services.rules_engine import RulesEngine
from backend.app.services.ml_engine import MLEngine
from backend.app.services.llm_engine import LLMEngine


class SpamDetector:
    def __init__(
        self,
        rules_engine: Optional[RulesEngine] = None,
        ml_engine: Optional[MLEngine] = None,
        llm_engine: Optional[LLMEngine] = None,
        use_llm: bool = True
    ):
        self.rules_engine = rules_engine or RulesEngine()
        self.ml_engine = ml_engine or MLEngine()
        self.llm_engine = llm_engine or LLMEngine()
        self.use_llm = use_llm

    def scan(self, text: str, sender_id: str = "", user_id: str = "anonymous") -> Dict[str, Any]:
        """Scans a short mobile text message across all three detection layers."""
        cleaned_text = text.strip()
        if not cleaned_text:
            return {
                "label": "SAFE",
                "confidence": 0.0,
                "risk_score": 0.0,
                "reasons": ["Empty message"],
                "layers_used": []
            }

        layers_used = []
        all_reasons = []

        # --- LAYER 1: RULES ENGINE ---
        l1_result = self.rules_engine.evaluate(cleaned_text, sender_id=sender_id)
        layers_used.append("Layer 1 (Rules Heuristics)")
        all_reasons.extend(l1_result["reasons"])
        l1_risk = l1_result["risk_score"]

        # CONTEXT RULE: If strict exemption applies and zero scam risk found, output SAFE immediately
        if l1_result["is_exempt_safe"] and l1_risk == 0.0:
            return {
                "label": "SAFE",
                "confidence": 0.98,
                "risk_score": 0.0,
                "reasons": all_reasons,
                "layers_used": layers_used,
                "layer_breakdown": {
                    "layer1_rules": l1_result,
                    "layer2_ml": None,
                    "layer3_llm": None
                }
            }

        # --- LAYER 2: ML INFERENCE ---
        l2_result = self.ml_engine.predict(cleaned_text)
        layers_used.append("Layer 2 (TF-IDF + Calibrated Classifier)")
        ml_prob = l2_result["ml_probability_spam"]

        # --- LAYER 3: LLM SECOND OPINION (Only when ML is ambiguous: 0.35 to 0.65) ---
        l3_result = None
        if self.use_llm and l2_result["is_ambiguous"] and not l1_result["is_exempt_safe"]:
            layers_used.append("Layer 3 (Groq LLM Second Opinion)")
            l3_result = self.llm_engine.get_second_opinion(cleaned_text, user_id=user_id)
            if l3_result and "reason" in l3_result:
                all_reasons.append(f"AI Second Opinion: {l3_result['reason']}")

        # --- WEIGHTED ARBITRATION ---
        # If Layer 1 detected explicit dangerous heuristics (e.g. IP link, APK download, credential theft)
        if l1_risk >= 0.75:
            combined_risk = 0.55 * l1_risk + 0.45 * ml_prob
            final_label = "SPAM"
            confidence = max(combined_risk, 0.85)

        # If Layer 3 provided an opinion
        elif l3_result and "label" in l3_result and "confidence" in l3_result:
            l3_label = l3_result["label"]
            l3_conf = l3_result["confidence"]

            if l3_label == "SPAM":
                combined_risk = 0.30 * l1_risk + 0.35 * ml_prob + 0.35 * l3_conf
                final_label = "SPAM" if combined_risk >= 0.60 else "SUSPICIOUS"
                confidence = combined_risk
            elif l3_label == "SAFE":
                combined_risk = 0.20 * l1_risk + 0.40 * ml_prob + 0.40 * (1.0 - l3_conf)
                final_label = "SAFE" if combined_risk <= 0.35 else "SUSPICIOUS"
                confidence = 1.0 - combined_risk
            else:
                combined_risk = 0.30 * l1_risk + 0.70 * ml_prob
                final_label = "SUSPICIOUS"
                confidence = 0.55

        # Standard combination of Layer 1 and Layer 2
        else:
            if l1_risk > 0:
                combined_risk = 0.40 * l1_risk + 0.60 * ml_prob
            else:
                combined_risk = ml_prob
            if combined_risk >= 0.65:
                final_label = "SPAM"
                confidence = combined_risk
            elif combined_risk <= 0.35:
                final_label = "SAFE"
                confidence = 1.0 - combined_risk
            else:
                final_label = "SUSPICIOUS"
                confidence = 0.60
                if not all_reasons:
                    all_reasons.append("Borderline promotional or unverified commercial message pattern")

        # Context safety override: If message is an educational warning or transactional without suspicious links, cap risk
        if l1_result["is_exempt_safe"]:
            final_label = "SAFE"
            confidence = max(confidence, 0.90)
            combined_risk = min(combined_risk, 0.10)

        # Default reason if empty
        if not all_reasons:
            if final_label == "SAFE":
                all_reasons.append("Normal conversational or transactional mobile message text")
            elif final_label == "SPAM":
                all_reasons.append("High probability mobile spam / scam linguistic signals")
            else:
                all_reasons.append("Unverified promotional or ambiguous message")

        return {
            "label": final_label,
            "confidence": round(confidence, 3),
            "risk_score": round(combined_risk, 3),
            "reasons": list(dict.fromkeys(all_reasons)),  # deduplicate preserving order
            "layers_used": layers_used,
            "layer_breakdown": {
                "layer1_rules": l1_result,
                "layer2_ml": l2_result,
                "layer3_llm": l3_result
            }
        }
