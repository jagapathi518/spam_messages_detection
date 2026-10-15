# Data Sources and Licenses

This document outlines all datasets used in the training, validation, and evaluation of **Spam Shield**.

> **Scope Note**: In accordance with project requirements, **only short mobile SMS and instant chat messages** are included. All email datasets, email-specific headers, and email terminology are strictly excluded.

---

## 1. UCI SMS Spam Collection Dataset
- **Description**: Publicly available corpus of 5,574 English mobile phone SMS messages, labeled as `ham` (legitimate) or `spam`.
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Source**: [UCI Machine Learning Repository / Almeida et al.](https://archive.ics.uci.edu/dataset/228/sms+spam+collection)
- **Role in Spam Shield**: Base mobile SMS collection providing baseline conversational ham and international commercial SMS spam patterns.
- **Preprocessing**: Normalized to `text`, `label` (`SAFE` / `SPAM`), and `source` (`uci_sms_collection`). Short message length filter (<800 characters) applied.

---

## 2. Synthetic Indian & Hinglish Mobile SMS Dataset
- **Description**: 1,479 domain-specific synthetic SMS and chat messages generated via Groq LLM (`qwen/qwen3.8-27b` and `openai/gpt-oss-20b`) plus generative template permutations.
- **Coverage**:
  - **Spam**: SBI/HDFC KYC scams, UPI cashback/refund scams, e-challan traffic notices, electricity disconnection threats, India Post/courier delivery scams, KBC/lottery prizes, part-time WFH Telegram jobs, instant 0-CIBIL loan scams, obfuscated spam (`fr33`, `cl!ck`, `wh@ts@pp`), brand lookalike promotions.
  - **Safe**: Bank debit/credit transactional alerts, genuine multi-factor OTPs (Aadhaar, Swiggy, Amazon, Zomato), delivery tracking updates, mobile recharge notifications, doctor/service appointment reminders, casual Hinglish chats, scam warning/educational notices, IRCTC PNR updates, legitimate brand promotions.
- **License**: Generated under custom project terms; open for non-commercial research and production use.
- **Role in Spam Shield**: **TRAINING ONLY** (`source="synthetic"`). Strictly excluded from validation and test splits to guarantee honest, unbiased generalization metrics.

---

## 3. Real-World Evaluation Benchmark (`real_world_test.csv`)
- **Description**: 221 carefully crafted out-of-sample real-world test cases spanning 18 distinct short-message categories and three difficulty tiers (`easy`, `medium`, `hard`).
- **Strict Constraint**: **NEVER** used in training, hyperparameter optimization, or threshold calibration. A mandatory automated test (`ml/tests/test_ml_integrity.py`) asserts zero text overlap between the training corpus and this benchmark.
- **Purpose**: Provable evaluation of the multi-layer detection engine against realistic threats and delicate false-positive edge cases (such as legitimate bank alerts, OTPs, and scam warning advisories).
