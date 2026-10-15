# Spam Shield: Primary Resume Highlight & Interview Guide

This document is crafted specifically for software engineering and machine learning interview preparation, detailing the technical depth, measured metrics, and architectural trade-offs of the **Spam Shield** project.

---

## 1. Resume Bullet Points (Copy & Paste)

```markdown
• Engineered "Spam Shield", an end-to-end mobile scam & phishing defense system with Flutter, FastAPI, Scikit-learn, and Groq LLMs, achieving 100% detection accuracy on a 221-message real-world telecom benchmark with a 0.44% False Positive Rate.
• Architected a 3-layer defense pipeline (Rules Heuristics -> TF-IDF Logistic Regression -> Groq LLM Second Opinion) with strict context exemptions to guarantee legitimate bank transactional alerts and OTPs are never falsely flagged.
• Optimized ML inference latency from 4.5s down to 2.2ms and memory consumption to 2.5MB by decomposing pickled model artifacts into lean sparse NumPy structures (weights.npz), bypassing Python 3.14 deserialization bottlenecks.
• Integrated dynamic LLM arbitration via Groq (Qwen-27B) triggered exclusively on borderline confidence intervals (0.35–0.65), featuring SHA-256 caching and per-user daily rate-limiting to minimize API costs and latency.
• Built automated CI/CD pipelines via GitHub Actions executing 18 automated unit/integrity tests and compiling release Android APK binaries on every commit.
```

---

## 2. Measured Benchmark Metrics

| Metric | Target / Benchmark | Measured Result | Status |
| :--- | :--- | :--- | :--- |
| **5-Fold Cross Validation F1** | > 0.95 | **0.9818 (+/- 0.0032)** | Exceeded |
| **Test Set ROC-AUC** | > 0.98 | **0.9959** | Exceeded |
| **Test Set PR-AUC** | > 0.95 | **0.9810** | Exceeded |
| **False Positive Rate (FPR)** | < 1.0% | **0.44%** | Exceeded |
| **Real-World Test Accuracy (221 msgs)** | > 95% | **100.00% (221/221)** | Exceeded |
| **Real-World Spam Recall** | > 95% | **100.00% (119/119)** | Exceeded |
| **Real-World Transactional Safety** | 100% | **100.00% (0/102 FP)** | Exceeded |
| **Model Load Time** | < 2.0s | **0.019s (19ms)** | 100x faster |
| **Steady-State ML Inference Latency** | < 50ms | **2.2ms** | 20x faster |
| **Memory Footprint (RAM)** | < 300MB | **2.5MB** | 120x leaner |

---

## 3. Interview Talking Points (STAR Method)

### Situation
Mobile telecommunication scams in India and emerging markets have evolved rapidly beyond simple email spam into targeted SMS and chat vectors: bank account freeze threats, fake electricity bill disconnection warnings, traffic e-challan malware APKs, and UPI lottery fraud. Traditional spam filters often rely on bulky deep learning models with high latency or overly broad heuristics that mistakenly block vital bank debit alerts and OTPs.

### Task
Design, build, and benchmark an end-to-end mobile application and backend system that detects short mobile text messages (SMS, WhatsApp, Telegram) with sub-5ms latency, memory footprint <300MB, zero false positives on genuine banking alerts, and explainable human-readable reasoning.

### Action
1. **Curated Clean Mobile Dataset:** Combined 5,129 clean base SMS messages with 1,479 balanced synthetic Indian scam/legit messages, creating a rigorously isolated 221-message real-world held-out benchmark with zero data leakage across 18 threat categories.
2. **Built 3-Layer Cascaded Pipeline:**
   - *Layer 1 (Rules):* Obfuscation decoder (`$B1` -> `sbi`) and URL/IP/APK inspector coupled with strict transactional exemptions.
   - *Layer 2 (ML):* Calibrated Logistic Regression with 28,450 word & character n-grams.
   - *Layer 3 (LLM):* Groq LLM second opinion invoked only when ML confidence is ambiguous (`0.35 - 0.65`).
3. **Solved Critical Deserialization Bottleneck:** Encountered >4-second loading times when loading scikit-learn pickled pipelines on Python 3.14 due to internal NumPy shape validation. Solved by decomposing model weights into a sparse `weights.npz` array and pure JSON vocabulary, reducing loading time to **19ms** and inference to **2.2ms**.
4. **Developed Flutter Client:** Built a responsive Material 3 mobile app with live animated risk meters, single message scanning, batch inbox scanning, an educational threat library, scan history, and user feedback reporting.

### Result
Achieved **100% accuracy** on the held-out real-world test benchmark with a **0.0% false positive rate on legitimate transactional messages**. Deployed FastAPI microservice with Supabase telemetry and automated GitHub Actions CI/CD.

---

## 4. Key Technical Questions & Answers

#### Q: Why not use a Transformer like BERT or RoBERTa?
> "In mobile telecom defense, inference latency and resource constraints are paramount. A MobileBERT or DistilBERT model requires >150MB disk space, >400MB RAM, and incurs 50–120ms CPU latency. Our calibrated n-gram Logistic Regression model delivers **0.9959 ROC-AUC** with **2.2ms** CPU latency and only **2.5MB** RAM. For the rare borderline cases (under 5% of traffic), we selectively trigger Groq LLMs as an asynchronous second opinion."

#### Q: How do you prevent legitimate bank OTPs and debit alerts from being flagged as spam?
> "We implemented deterministic Context Rules in Layer 1. The engine checks for structural financial patterns: masked account numbers (`A/c XX1234`), balance updates (`Avail Bal:`), and registered customer service numbers. If a message matches genuine transactional syntax and contains no suspicious URLs, APK downloads, or IP addresses, it is strictly exempted and verified as SAFE in <0.2ms."

#### Q: How does the system adapt to new emerging scams?
> "Users can report false alarms or missed scams directly from the Flutter app via `/api/v1/feedback`. These records are stored in Supabase and ingested by `ml/src/retrain.py`, which validates corrections, merges them into the continuous learning set, and retrains the calibrated classifier without downtime."
