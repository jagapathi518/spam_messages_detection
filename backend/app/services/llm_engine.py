"""Layer 3: Groq LLM Second Opinion Engine.

Only invoked when Layer 2 ML probability falls in the ambiguous window [0.35, 0.65].
Includes:
- Hash-based caching via Supabase or local in-memory fallback.
- Daily per-user call rate limiting.
- Strict 5-second timeout.
- Graceful degradation fallback to Layers 1 + 2 on any API error or timeout.
"""
import os
import json
import time
import hashlib
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from groq import Groq

# Load environment
load_dotenv()


class LLMEngine:
    def __init__(self, supabase_client=None):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.primary_model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        self.fallback_model = os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-20b")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.supabase = supabase_client
        self._local_cache: Dict[str, Dict[str, Any]] = {}
        self._user_call_counts: Dict[str, Dict[str, int]] = {}
        self.daily_limit = int(os.getenv("RATE_LIMIT_GROQ_PER_USER_PER_DAY", 50))

    def _hash_message(self, text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()

    def _check_rate_limit(self, user_id: str) -> bool:
        today = time.strftime("%Y-%m-%d")
        if user_id not in self._user_call_counts:
            self._user_call_counts[user_id] = {"date": today, "count": 0}
        
        user_record = self._user_call_counts[user_id]
        if user_record["date"] != today:
            user_record["date"] = today
            user_record["count"] = 0

        if user_record["count"] >= self.daily_limit:
            return False  # Rate limit exceeded

        user_record["count"] += 1
        return True

    def _get_cached_opinion(self, msg_hash: str) -> Optional[Dict[str, Any]]:
        # 1. In-memory cache
        if msg_hash in self._local_cache:
            return self._local_cache[msg_hash]

        # 2. Supabase cache
        if self.supabase:
            try:
                res = self.supabase.table("llm_cache").select("*").eq("message_hash", msg_hash).execute()
                if res.data and len(res.data) > 0:
                    cached = {
                        "label": res.data[0]["label"],
                        "confidence": float(res.data[0]["confidence"]),
                        "reason": res.data[0]["reason"],
                        "cached": True
                    }
                    self._local_cache[msg_hash] = cached
                    return cached
            except Exception:
                pass
        return None

    def _save_cached_opinion(self, msg_hash: str, text: str, opinion: Dict[str, Any]):
        self._local_cache[msg_hash] = opinion
        if self.supabase:
            try:
                self.supabase.table("llm_cache").insert({
                    "message_hash": msg_hash,
                    "text_preview": text[:100],
                    "label": opinion["label"],
                    "confidence": opinion["confidence"],
                    "reason": opinion["reason"]
                }).execute()
            except Exception:
                pass

    def get_second_opinion(self, text: str, user_id: str = "anonymous") -> Optional[Dict[str, Any]]:
        """Queries Groq LLM with a 5s timeout, caching, and rate limiting."""
        if not self.client:
            return None

        # Check rate limit
        if not self._check_rate_limit(user_id):
            return {
                "label": "SUSPICIOUS",
                "confidence": 0.50,
                "reason": "User daily Groq LLM second opinion rate limit reached",
                "error": "rate_limited"
            }

        # Check cache
        msg_hash = self._hash_message(text)
        cached = self._get_cached_opinion(msg_hash)
        if cached:
            return cached

        system_prompt = (
            "You are a mobile telecom cybersecurity expert. Analyze this SHORT mobile SMS/chat message. "
            "Return ONLY a JSON object with keys: "
            "'label' ('SPAM', 'SUSPICIOUS', or 'SAFE'), "
            "'confidence' (float between 0.0 and 1.0), "
            "'reason' (a concise 1-sentence explanation of why)."
        )
        user_prompt = f"SMS Message to analyze:\n\"{text}\""

        models_to_try = [self.primary_model, self.fallback_model, "llama-3.1-8b-instant"]

        for model in models_to_try:
            try:
                t0 = time.time()
                resp = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=model,
                    response_format={"type": "json_object"},
                    max_tokens=150,
                    timeout=5.0  # 5-second strict timeout
                )
                content = resp.choices[0].message.content
                data = json.loads(content)

                label = data.get("label", "SUSPICIOUS").upper()
                if label not in ["SPAM", "SUSPICIOUS", "SAFE"]:
                    label = "SUSPICIOUS"

                confidence = float(data.get("confidence", 0.60))
                reason = data.get("reason", "Ambiguous telecom message structure")

                result = {
                    "label": label,
                    "confidence": round(confidence, 3),
                    "reason": reason,
                    "model_used": model,
                    "latency_ms": round((time.time() - t0) * 1000.0, 2)
                }

                # Save to cache
                self._save_cached_opinion(msg_hash, text, result)
                return result

            except Exception:
                continue

        # If all models fail, return None to trigger graceful fallback to layers 1+2
        return None
