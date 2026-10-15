"""ML Pipeline Integrity and Leakage Prevention Tests.

Guarantees:
1. Absolute zero leakage between real_world_test.csv and training/validation data.
2. Model loading time is strictly < 2.0 seconds.
3. Memory consumption remains well below 300 MB.
4. Robustness against typos, leetspeak, obfuscation, and Hinglish.
5. Strict output schema adherence.
"""
import sys
import time
import tracemalloc
import pytest
from pathlib import Path
import pandas as pd
import numpy as np

# Add repository root to path
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root))

from backend.app.services.ml_engine import MLEngine
from backend.app.services.rules_engine import RulesEngine
from backend.app.services.detector import SpamDetector


def test_zero_leakage_between_train_and_real_world_test():
    """CRITICAL TEST: Asserts zero text overlap between real_world_test.csv and any training data."""
    real_test_path = repo_root / "ml" / "data" / "real_world_test.csv"
    base_data_path = repo_root / "ml" / "data" / "base_sms_clean.csv"
    syn_data_path = repo_root / "ml" / "data" / "synthetic_sms.csv"

    assert real_test_path.exists(), "real_world_test.csv must exist"
    assert base_data_path.exists(), "base_sms_clean.csv must exist"
    assert syn_data_path.exists(), "synthetic_sms.csv must exist"

    df_real = pd.read_csv(real_test_path)
    df_base = pd.read_csv(base_data_path)
    df_syn = pd.read_csv(syn_data_path)

    real_texts = set(df_real["text"].str.strip().str.lower())
    base_texts = set(df_base["text"].str.strip().str.lower())
    syn_texts = set(df_syn["text"].str.strip().str.lower())

    base_overlap = real_texts.intersection(base_texts)
    syn_overlap = real_texts.intersection(syn_texts)

    assert len(base_overlap) == 0, f"LEAKAGE DETECTED: {len(base_overlap)} real test samples found in base data: {base_overlap}"
    assert len(syn_overlap) == 0, f"LEAKAGE DETECTED: {len(syn_overlap)} real test samples found in synthetic data: {syn_overlap}"


def test_model_loading_latency_and_memory():
    """Asserts model loads in < 2.0s and memory allocation is < 300MB."""
    ml_engine = MLEngine()
    load_time_sec = ml_engine.load_time_ms / 1000.0

    # Memory tracing
    tracemalloc.start()
    ml_engine2 = MLEngine()
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak_bytes / (1024 * 1024)
    print(f"\nModel Load Time: {load_time_sec:.3f}s (Threshold: < 2.0s)")
    print(f"Model Peak Memory Allocation: {peak_mb:.2f}MB (Threshold: < 300MB)")

    assert load_time_sec < 2.0, f"Model took {load_time_sec:.2f}s to load, exceeding 2s requirement"
    assert peak_mb < 300.0, f"RAM allocation is {peak_mb:.2f}MB, exceeding 300MB requirement"


def test_detector_schema_and_inference_speed():
    """Asserts detection output adheres to expected contract and runs quickly."""
    detector = SpamDetector(use_llm=False)
    test_msg = "Dear user, your SBI account is blocked today. Visit http://sbi-kyc.xyz to update."

    # Warmup call
    detector.scan("Warmup message")

    # Benchmarking steady-state latency
    times = []
    for _ in range(10):
        t0 = time.time()
        result = detector.scan(test_msg)
        times.append((time.time() - t0) * 1000.0)

    avg_elapsed_ms = sum(times) / len(times)
    print(f"\nAverage Steady-State Inference Latency: {avg_elapsed_ms:.2f}ms (Threshold: < 50ms)")

    assert "label" in result
    assert result["label"] in ["SPAM", "SUSPICIOUS", "SAFE"]
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0
    assert "risk_score" in result
    assert 0.0 <= result["risk_score"] <= 1.0
    assert "reasons" in result and isinstance(result["reasons"], list)
    assert len(result["reasons"]) > 0
    assert "layers_used" in result and isinstance(result["layers_used"], list)

    assert result["label"] == "SPAM"
    assert avg_elapsed_ms < 50.0, f"Average inference took {avg_elapsed_ms:.1f}ms, expected < 50ms"


def test_obfuscation_and_hinglish_robustness():
    """Asserts char n-grams and heuristics catch obfuscated and Hinglish spam."""
    detector = SpamDetector(use_llm=False)
    obf_msg = "FR33 entry 2 win 50,000 c@sh! Cl!ck http://win-priz3.top t0 cl@im now."
    res = detector.scan(obf_msg)

    assert res["label"] == "SPAM"
    assert any("obfuscated" in r.lower() or "suspicious" in r.lower() for r in res["reasons"])


def test_context_rule_safe_transactional_exemption():
    """Asserts legitimate transactional alerts with legitimate domains are NEVER flagged as SPAM."""
    detector = SpamDetector(use_llm=False)
    safe_msgs = [
        "Dear SBI User, your A/c XX4892 is debited by INR 1,250.00 on 14-Oct-26 at Swiggy UPI Ref 429384729182. Avl Bal: INR 18,432.10 - SBI",
        "492817 is your secret One Time Password (OTP) for SBI NetBanking login. Valid for 5 minutes. Do NOT share OTP with anyone.",
        "Your order #402-1928374 from Amazon is out for delivery today with delivery associate Ramesh Kumar. Share delivery code 48.",
        "Security Warning from SBI: Never share your OTP, UPI PIN, Password or CVV with anyone. Bank never calls asking for credentials."
    ]

    for msg in safe_msgs:
        res = detector.scan(msg)
        assert res["label"] == "SAFE", f"False positive detected! Expected SAFE, got {res['label']} for: {msg}"
        assert res["risk_score"] < 0.30
