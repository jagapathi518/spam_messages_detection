"""Layer 2: ML Inference Engine for Mobile Short Text Message Detection.

Uses trained TF-IDF (word 1-2 + char 2-5) + Calibrated Logistic Regression.
Ensures ultra-fast load time (<0.1s) and low memory (<50MB).
No deep learning dependencies at inference time.
"""
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import scipy.sparse as sp
import joblib


class MLEngine:
    def __init__(self, artifacts_dir: Optional[Path] = None):
        if artifacts_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            artifacts_dir = base_dir.parent / "ml" / "artifacts"
            if not artifacts_dir.exists():
                artifacts_dir = base_dir / "artifacts"

        self.artifacts_dir = artifacts_dir
        self.word_vec = None
        self.char_vec = None
        self.vectorizer = None
        self.coef = None
        self.intercept = None
        self.metadata = {}
        self.optimal_threshold = 0.50
        self.load_time_ms = 0.0
        self._load_artifacts()

    def _load_artifacts(self):
        t0 = time.time()
        import pickle

        weights_path = self.artifacts_dir / "weights.npz"
        vec_pkl = self.artifacts_dir / "vectorizer.pkl"
        vec_joblib = self.artifacts_dir / "vectorizer.joblib"
        meta_path = self.artifacts_dir / "metadata.json"

        # 1. Load Vectorizers (w_vocab.json + char_vec.pkl loads in ~0.02s)
        w_vocab_path = self.artifacts_dir / "w_vocab.json"
        char_vec_path = self.artifacts_dir / "char_vec.pkl"
        vec_pkl = self.artifacts_dir / "vectorizer.pkl"
        vec_joblib = self.artifacts_dir / "vectorizer.joblib"
        meta_path = self.artifacts_dir / "metadata.json"

        if w_vocab_path.exists() and char_vec_path.exists():
            with open(w_vocab_path, "r", encoding="utf-8") as f:
                w_data = json.load(f)
            self.word_vec = TfidfVectorizer(ngram_range=(1, 2), vocabulary=w_data["vocab"])
            self.word_vec.idf_ = np.array(w_data["idf"])

            with open(char_vec_path, "rb") as f:
                self.char_vec = pickle.load(f)
        elif vec_pkl.exists():
            with open(vec_pkl, "rb") as f:
                self.vectorizer = pickle.load(f)
        elif vec_joblib.exists():
            self.vectorizer = joblib.load(vec_joblib)
        else:
            raise FileNotFoundError(f"Missing vectorizer artifact in {self.artifacts_dir}")

        # 2. Load Model weights (weights.npz is ~6ms)
        if weights_path.exists():
            weights = np.load(weights_path)
            self.coef = weights["coef"]
            self.intercept = weights["intercept"]
        else:
            model_pkl = self.artifacts_dir / "model.pkl"
            model_joblib = self.artifacts_dir / "model.joblib"
            if model_pkl.exists():
                with open(model_pkl, "rb") as f:
                    model = pickle.load(f)
            elif model_joblib.exists():
                model = joblib.load(model_joblib)
            else:
                raise FileNotFoundError(f"Missing model artifact in {self.artifacts_dir}")
            self.coef = getattr(model, "coef_", None)
            self.intercept = getattr(model, "intercept_", None)

        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            self.optimal_threshold = self.metadata.get("optimal_threshold", 0.50)

        self.load_time_ms = (time.time() - t0) * 1000.0

    def predict(self, text: str) -> Dict[str, Any]:
        """Runs vectorization and calibrated probability prediction on a single text."""
        t0 = time.time()

        # Vectorize
        if self.word_vec is not None and self.char_vec is not None:
            x_w = self.word_vec.transform([text])
            x_c = self.char_vec.transform([text])
            vec = sp.hstack([x_w, x_c], format="csr")
        elif self.vectorizer is not None:
            vec = self.vectorizer.transform([text])
        else:
            raise RuntimeError("Vectorizer not properly loaded.")

        # Fast direct sigmoid calculation: P(SPAM) = 1 / (1 + exp(-(X * W + b)))
        if self.coef is not None and self.intercept is not None:
            raw_score = float(vec.dot(self.coef.T)[0, 0] + self.intercept[0])
            prob_spam = float(1.0 / (1.0 + np.exp(-raw_score)))
        else:
            prob_spam = 0.50

        # Classification based on threshold & ambiguity boundaries
        if prob_spam >= 0.65:
            ml_label = "SPAM"
        elif prob_spam <= 0.35:
            ml_label = "SAFE"
        else:
            ml_label = "SUSPICIOUS"

        elapsed_ms = (time.time() - t0) * 1000.0

        return {
            "ml_probability_spam": round(prob_spam, 4),
            "ml_label": ml_label,
            "latency_ms": round(elapsed_ms, 2),
            "is_ambiguous": 0.35 <= prob_spam <= 0.65
        }

    def is_ready(self) -> bool:
        """Returns True if the ML weights and vectorizers are loaded."""
        return self.coef is not None and (self.word_vec is not None or self.vectorizer is not None)

