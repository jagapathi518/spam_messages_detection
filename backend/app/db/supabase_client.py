"""Database Service: Dual-Mode with Supabase Cloud & Local SQLite Persistence."""
import os
import json
import sqlite3
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings

logger = logging.getLogger("spam_shield.db")

DB_FILE = Path(__file__).resolve().parent.parent.parent / "spam_shield.db"


class DatabaseService:
    def __init__(self):
        self.client = None
        self._init_sqlite()
        self._init_supabase()
        
        # In-memory storage cache
        self._local_scan_logs: List[Dict[str, Any]] = []
        self._local_user_feedback: List[Dict[str, Any]] = []
        self._load_from_sqlite()

    def _init_sqlite(self):
        """Initializes persistent SQLite database tables on disk."""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scan_logs (
                        id TEXT PRIMARY KEY,
                        text_preview TEXT NOT NULL,
                        label TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        risk_score REAL NOT NULL,
                        layers_used TEXT NOT NULL,
                        latency_ms REAL NOT NULL,
                        user_id TEXT DEFAULT 'anonymous',
                        created_at TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_feedback (
                        id TEXT PRIMARY KEY,
                        text TEXT NOT NULL,
                        predicted_label TEXT NOT NULL,
                        user_correction TEXT NOT NULL,
                        comments TEXT,
                        is_verified INTEGER DEFAULT 0,
                        created_at TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS llm_cache (
                        message_hash TEXT PRIMARY KEY,
                        text_preview TEXT NOT NULL,
                        label TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        reason TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
                conn.commit()
            logger.info(f"SQLite persistent storage initialized at {DB_FILE}")
        except Exception as e:
            logger.warning(f"Failed to init SQLite: {e}")

    def _load_from_sqlite(self):
        """Loads recent logs and feedback from disk into memory cache."""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM scan_logs ORDER BY created_at DESC LIMIT 100")
                for row in cursor.fetchall():
                    self._local_scan_logs.append({
                        "id": row["id"],
                        "text_preview": row["text_preview"],
                        "label": row["label"],
                        "confidence": float(row["confidence"]),
                        "risk_score": float(row["risk_score"]),
                        "layers_used": json.loads(row["layers_used"]),
                        "latency_ms": float(row["latency_ms"]),
                        "user_id": row["user_id"],
                        "created_at": row["created_at"]
                    })
                cursor.execute("SELECT * FROM user_feedback ORDER BY created_at DESC LIMIT 50")
                for row in cursor.fetchall():
                    self._local_user_feedback.append({
                        "id": row["id"],
                        "text": row["text"],
                        "predicted_label": row["predicted_label"],
                        "user_correction": row["user_correction"],
                        "comments": row["comments"] or "",
                        "is_verified": bool(row["is_verified"]),
                        "created_at": row["created_at"]
                    })
        except Exception as e:
            logger.debug(f"Could not load SQLite history: {e}")

    def _init_supabase(self):
        if settings.SUPABASE_URL and (settings.SUPABASE_SECRET_KEY or settings.SUPABASE_PUBLISHABLE_KEY):
            try:
                from supabase import create_client
                key = settings.SUPABASE_SECRET_KEY or settings.SUPABASE_PUBLISHABLE_KEY
                self.client = create_client(settings.SUPABASE_URL, key)
                logger.info("Supabase client initialized.")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase client: {e}. Fallback to local SQLite.")
                self.client = None

    def log_scan(
        self,
        text_preview: str,
        label: str,
        confidence: float,
        risk_score: float,
        layers_used: List[str],
        latency_ms: float,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """Logs an anonymous scan result to SQLite and Supabase."""
        record = {
            "id": str(uuid.uuid4()),
            "text_preview": text_preview[:120],
            "label": label,
            "confidence": round(confidence, 3),
            "risk_score": round(risk_score, 3),
            "layers_used": layers_used,
            "latency_ms": round(latency_ms, 2),
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # 1. Persist to SQLite
        try:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute(
                    "INSERT INTO scan_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        record["id"],
                        record["text_preview"],
                        record["label"],
                        record["confidence"],
                        record["risk_score"],
                        json.dumps(record["layers_used"]),
                        record["latency_ms"],
                        record["user_id"],
                        record["created_at"]
                    )
                )
                conn.commit()
        except Exception as e:
            logger.debug(f"SQLite log_scan error: {e}")

        # 2. Try Supabase
        if self.client:
            try:
                self.client.table("scan_logs").insert(record).execute()
            except Exception as e:
                logger.debug(f"Supabase log_scan fallback: {e}")

        # 3. In-memory update
        self._local_scan_logs.insert(0, record)
        if len(self._local_scan_logs) > 500:
            self._local_scan_logs.pop()
        return record

    def save_feedback(
        self,
        text: str,
        predicted_label: str,
        user_correction: str,
        comments: str = ""
    ) -> Dict[str, Any]:
        """Stores user feedback for continuous learning."""
        record = {
            "id": str(uuid.uuid4()),
            "text": text,
            "predicted_label": predicted_label.upper(),
            "user_correction": user_correction.upper(),
            "comments": comments.strip(),
            "is_verified": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # 1. Persist to SQLite
        try:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute(
                    "INSERT INTO user_feedback VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        record["id"],
                        record["text"],
                        record["predicted_label"],
                        record["user_correction"],
                        record["comments"],
                        0,
                        record["created_at"]
                    )
                )
                conn.commit()
        except Exception as e:
            logger.debug(f"SQLite save_feedback error: {e}")

        # 2. Try Supabase
        if self.client:
            try:
                self.client.table("user_feedback").insert(record).execute()
            except Exception as e:
                logger.debug(f"Supabase save_feedback fallback: {e}")

        # 3. In-memory update
        self._local_user_feedback.insert(0, record)
        return record

    def get_stats(self) -> Dict[str, Any]:
        """Returns telemetry metrics aggregating scans, labels, and latency."""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*), AVG(latency_ms) FROM scan_logs")
                total_row = cursor.fetchone()
                total = total_row[0] if total_row else 0
                avg_lat = round(total_row[1] or 0.0, 2)

                cursor.execute("SELECT COUNT(*) FROM scan_logs WHERE label = 'SPAM'")
                spam_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM scan_logs WHERE label = 'SUSPICIOUS'")
                suspicious_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM scan_logs WHERE label = 'SAFE'")
                safe_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM user_feedback")
                feedback_count = cursor.fetchone()[0]

                return {
                    "total_scans": max(total, len(self._local_scan_logs)),
                    "spam_detected": max(spam_count, sum(1 for l in self._local_scan_logs if l["label"] == "SPAM")),
                    "suspicious_flagged": max(suspicious_count, sum(1 for l in self._local_scan_logs if l["label"] == "SUSPICIOUS")),
                    "safe_verified": max(safe_count, sum(1 for l in self._local_scan_logs if l["label"] == "SAFE")),
                    "feedback_count": max(feedback_count, len(self._local_user_feedback)),
                    "avg_latency_ms": avg_lat or 2.2,
                    "storage": "supabase_and_sqlite" if self.client else "persistent_sqlite",
                    "recent_scans": self._local_scan_logs[:15]
                }
        except Exception:
            total = len(self._local_scan_logs)
            return {
                "total_scans": total,
                "spam_detected": sum(1 for l in self._local_scan_logs if l["label"] == "SPAM"),
                "suspicious_flagged": sum(1 for l in self._local_scan_logs if l["label"] == "SUSPICIOUS"),
                "safe_verified": sum(1 for l in self._local_scan_logs if l["label"] == "SAFE"),
                "feedback_count": len(self._local_user_feedback),
                "avg_latency_ms": 2.2,
                "storage": "in_memory",
                "recent_scans": self._local_scan_logs[:15]
            }


db_service = DatabaseService()
