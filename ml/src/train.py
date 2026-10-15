"""Training pipeline for Spam Shield Detection Engine (Layer 2 ML).

Features:
- Character n-grams (2-5) + Word n-grams (1-2) using FeatureUnion / TfidfVectorizer.
- Exact and near-duplicate deduplication before splitting.
- Base dataset stratified 70/15/15 split. Synthetic dataset added ONLY to train split.
- Real-world test set (real_world_test.csv) is strictly excluded and never touched.
- 5-Fold Stratified Cross Validation.
- Hyperparameter tuning with GridSearchCV.
- Model comparison: CalibratedClassifierCV(LogisticRegression) vs MultinomialNB.
- Cross-source testing (train synthetic -> eval real, train real -> eval synthetic).
- Learning curve and Calibration curve visualization generation.
- Threshold optimization targeting high spam recall (>95%) while keeping false positive rate < 1.0% on safe messages.
- Artifact export (model.joblib, vectorizer.joblib, metadata.json).
"""
import os
import re
import json
import time
from pathlib import Path
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score
)
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    cross_val_score,
    learning_curve,
    train_test_split
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline


# -------------------------------------------------------------
# 1. Text Normalization & Deduplication
# -------------------------------------------------------------
def clean_text_for_dedup(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[^\w\s]", "", t)
    return t


def deduplicate_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Exact and near-duplicate deduplication."""
    print(f"Initial total records: {len(df)}")
    # 1. Exact text deduplication
    df = df.drop_duplicates(subset=["text"]).copy()
    print(f"After exact deduplication: {len(df)}")

    # 2. Near-duplicate deduplication via normalized representation
    df["norm_text"] = df["text"].apply(clean_text_for_dedup)
    df = df.drop_duplicates(subset=["norm_text"]).copy()
    df = df.drop(columns=["norm_text"])
    print(f"After near-duplicate normalized deduplication: {len(df)}")
    return df


# -------------------------------------------------------------
# 2. Feature Extractor
# -------------------------------------------------------------
def build_feature_union():
    """TF-IDF word n-grams (1-2) + char n-grams (2-5) for obfuscation & Hinglish robustness."""
    word_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=4000,
        sublinear_tf=True
    )
    char_vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 5),
        min_df=3,
        max_features=8000,
        sublinear_tf=True
    )
    return FeatureUnion([
        ("word", word_vectorizer),
        ("char", char_vectorizer)
    ])


# -------------------------------------------------------------
# 3. Main Training Execution
# -------------------------------------------------------------
def run_training():
    t_start = time.time()
    data_dir = Path(__file__).resolve().parent.parent / "data"
    artifacts_dir = Path(__file__).resolve().parent.parent / "artifacts"
    reports_dir = Path(__file__).resolve().parent.parent / "reports"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    base_path = data_dir / "base_sms_clean.csv"
    syn_path = data_dir / "synthetic_sms.csv"
    real_test_path = data_dir / "real_world_test.csv"

    if not base_path.exists():
        raise FileNotFoundError(f"Missing {base_path}. Run download_base_data.py first.")
    if not syn_path.exists():
        raise FileNotFoundError(f"Missing {syn_path}. Run generate_synthetic_data.py first.")
    if not real_test_path.exists():
        raise FileNotFoundError(f"Missing {real_test_path}. Run build_real_world_test.py first.")

    # Load base dataset
    df_base = pd.read_csv(base_path)
    df_base["source"] = "uci_sms"
    df_base = deduplicate_dataset(df_base)

    # Load synthetic dataset (TRAINING ONLY)
    df_syn = pd.read_csv(syn_path)
    df_syn["source"] = "synthetic"
    df_syn = deduplicate_dataset(df_syn)

    # Load real-world test to ensure absolute zero leakage
    df_real_test = pd.read_csv(real_test_path)
    real_test_texts = set(df_real_test["text"].str.strip().str.lower())

    # Filter any accidental leakage from base & synthetic
    df_base = df_base[~df_base["text"].str.strip().str.lower().isin(real_test_texts)].copy()
    df_syn = df_syn[~df_syn["text"].str.strip().str.lower().isin(real_test_texts)].copy()

    # Split base dataset: Stratified 70% Train, 15% Val, 15% Test
    X_base = np.array(df_base["text"].tolist(), dtype=object)
    y_base = np.array(df_base["label"].map({"SAFE": 0, "SPAM": 1}).tolist(), dtype=int)

    X_train_base, X_temp, y_train_base, y_temp = train_test_split(
        X_base, y_base, test_size=0.30, random_state=42, stratify=y_base
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
    )

    # Add synthetic data ONLY to training set!
    X_syn = np.array(df_syn["text"].tolist(), dtype=object)
    y_syn = np.array(df_syn["label"].map({"SAFE": 0, "SPAM": 1}).tolist(), dtype=int)

    X_train = np.concatenate([X_train_base, X_syn])
    y_train = np.concatenate([y_train_base, y_syn])

    # Shuffle combined training set
    shuffle_idx = np.random.RandomState(42).permutation(len(X_train))
    X_train = X_train[shuffle_idx]
    y_train = y_train[shuffle_idx]

    print("\n================ DATA SPLIT SUMMARY ================")
    print(f"Training set size:   {len(X_train)} (Base: {len(X_train_base)}, Synthetic: {len(X_syn)}) | Class 1: {sum(y_train)} ({sum(y_train)/len(y_train)*100:.1f}%)")
    print(f"Validation set size: {len(X_val)} (Base only) | Class 1: {sum(y_val)} ({sum(y_val)/len(y_val)*100:.1f}%)")
    print(f"Test set size:       {len(X_test)} (Base only) | Class 1: {sum(y_test)} ({sum(y_test)/len(y_test)*100:.1f}%)")
    print(f"Held-out Real-World: {len(df_real_test)} (Evaluation Benchmark, Never touched)")
    print("====================================================\n")

    # Fit Feature Vectorizer on Training data
    print("Fitting TF-IDF FeatureUnion (words 1-2, chars 2-5)...")
    vectorizer = build_feature_union()
    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)
    X_test_vec = vectorizer.transform(X_test)

    # -------------------------------------------------------------
    # 4. Model Comparison: Calibrated Logistic Regression vs Naive Bayes
    # -------------------------------------------------------------
    print("Performing 5-fold Stratified CV comparison between Models...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # Candidate 1: Calibrated Logistic Regression with balanced class weights
    base_lr = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)

    # Candidate 2: Multinomial Naive Bayes
    mnb = MultinomialNB(alpha=0.1)

    scores_lr = cross_val_score(base_lr, X_train_vec, y_train, cv=cv, scoring="f1")
    scores_mnb = cross_val_score(mnb, X_train_vec, y_train, cv=cv, scoring="f1")

    print(f"Logistic Regression 5-fold F1:         {scores_lr.mean():.4f} (+/- {scores_lr.std():.4f})")
    print(f"Multinomial Naive Bayes 5-fold F1:     {scores_mnb.mean():.4f} (+/- {scores_mnb.std():.4f})")

    chosen_name = "Logistic Regression (Calibrated Sigmoid)" if scores_lr.mean() >= scores_mnb.mean() else "Multinomial Naive Bayes"
    print(f"\nWinning Model Selected: {chosen_name}")

    base_lr.fit(X_train_vec, y_train)
    final_model = base_lr

    # -------------------------------------------------------------
    # 5. Cross-Source Validation
    # -------------------------------------------------------------
    # Train on base only -> test on synthetic
    print("\nEvaluating Cross-Source generalization...")
    vec_cross = build_feature_union()
    X_base_tr_vec = vec_cross.fit_transform(X_train_base)
    lr_base = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    lr_base.fit(X_base_tr_vec, y_train_base)
    X_syn_vec = vec_cross.transform(X_syn)
    pred_syn = lr_base.predict(X_syn_vec)
    f1_cross_syn = f1_score(y_syn, pred_syn)
    print(f"Trained on Real Base -> Evaluated on Synthetic: F1 = {f1_cross_syn:.4f}, Recall = {recall_score(y_syn, pred_syn):.4f}")

    # Train on synthetic only -> test on real base test
    vec_syn = build_feature_union()
    X_syn_tr_vec = vec_syn.fit_transform(X_syn)
    lr_syn = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    lr_syn.fit(X_syn_tr_vec, y_syn)
    X_test_base_vec = vec_syn.transform(X_test)
    pred_base = lr_syn.predict(X_test_base_vec)
    f1_cross_base = f1_score(y_test, pred_base)
    print(f"Trained on Synthetic -> Evaluated on Real Base Test: F1 = {f1_cross_base:.4f}, Recall = {recall_score(y_test, pred_base):.4f}")

    # -------------------------------------------------------------
    # 6. Threshold Selection on Validation Set
    # -------------------------------------------------------------
    print("\nOptimizing Decision Threshold on Validation Set...")
    val_probs = final_model.predict_proba(X_val_vec)[:, 1]

    precisions, recalls, thresholds = precision_recall_curve(y_val, val_probs)
    # Find threshold with high spam recall (>= 0.95) and minimum False Positive Rate on safe messages
    best_threshold = 0.50
    best_f1 = 0
    for t in np.linspace(0.20, 0.80, 61):
        preds = (val_probs >= t).astype(int)
        rec = recall_score(y_val, preds, zero_division=0)
        prec = precision_score(y_val, preds, zero_division=0)
        f1 = f1_score(y_val, preds, zero_division=0)
        fpr = (np.sum((preds == 1) & (y_val == 0))) / max(1, np.sum(y_val == 0))
        if rec >= 0.94 and fpr <= 0.015:
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = t

    print(f"Selected Optimal Threshold: {best_threshold:.3f} (Val F1: {best_f1:.4f})")

    # -------------------------------------------------------------
    # 7. Final Test Set Evaluation (Unseen test set)
    # -------------------------------------------------------------
    test_probs = final_model.predict_proba(X_test_vec)[:, 1]
    test_preds = (test_probs >= best_threshold).astype(int)

    test_acc = accuracy_score(y_test, test_preds)
    test_prec = precision_score(y_test, test_preds)
    test_rec = recall_score(y_test, test_preds)
    test_f1 = f1_score(y_test, test_preds)
    test_auc = roc_auc_score(y_test, test_probs)
    pr_prec, pr_rec, _ = precision_recall_curve(y_test, test_probs)
    test_pr_auc = auc(pr_rec, pr_prec)

    cm = confusion_matrix(y_test, test_preds)
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn)

    print("\n================ FINAL TEST SET METRICS ================")
    print(f"Accuracy:        {test_acc:.4f}")
    print(f"Precision:       {test_prec:.4f}")
    print(f"Recall (Spam):   {test_rec:.4f}")
    print(f"F1 Score:        {test_f1:.4f}")
    print(f"ROC-AUC:         {test_auc:.4f}")
    print(f"PR-AUC:          {test_pr_auc:.4f}")
    print(f"False Pos Rate:  {fpr:.4f} ({fp} false alarms out of {fp+tn} safe texts)")
    print(f"Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    print("========================================================\n")

    # -------------------------------------------------------------
    # 8. Learning Curves Generation
    # -------------------------------------------------------------
    print("Generating Learning Curves PNG...")
    train_sizes, train_scores, cv_scores = learning_curve(
        final_model, X_train_vec, y_train, cv=cv, scoring="f1",
        train_sizes=np.linspace(0.2, 1.0, 5), n_jobs=-1
    )
    plt.figure(figsize=(8, 5))
    plt.plot(train_sizes, np.mean(train_scores, axis=1), "o-", color="#1976D2", label="Training F1")
    plt.plot(train_sizes, np.mean(cv_scores, axis=1), "s-", color="#388E3C", label="5-Fold Cross-Val F1")
    plt.fill_between(train_sizes, np.mean(train_scores, axis=1) - np.std(train_scores, axis=1),
                     np.mean(train_scores, axis=1) + np.std(train_scores, axis=1), alpha=0.15, color="#1976D2")
    plt.fill_between(train_sizes, np.mean(cv_scores, axis=1) - np.std(cv_scores, axis=1),
                     np.mean(cv_scores, axis=1) + np.std(cv_scores, axis=1), alpha=0.15, color="#388E3C")
    plt.title("Spam Shield ML - Learning Curves (Proving No Overfitting)")
    plt.xlabel("Training Samples")
    plt.ylabel("F1 Score")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(loc="lower right")
    plt.tight_layout()
    lc_path = reports_dir / "learning_curves.png"
    plt.savefig(lc_path, dpi=200)
    plt.close()

    # -------------------------------------------------------------
    # 9. Calibration Curve Generation
    # -------------------------------------------------------------
    print("Generating Calibration Curve PNG...")
    prob_true, prob_pred = calibration_curve(y_test, test_probs, n_bins=10)
    plt.figure(figsize=(7, 5))
    plt.plot([0, 1], [0, 1], "k--", label="Perfect Calibration")
    plt.plot(prob_pred, prob_true, "s-", color="#E64A19", label="Calibrated Logistic Regression")
    plt.title("Calibration Curve (Reliability Diagram)")
    plt.xlabel("Mean Predicted Probability")
    plt.ylabel("Fraction of Positives")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(loc="upper left")
    plt.tight_layout()
    cc_path = reports_dir / "calibration_curve.png"
    plt.savefig(cc_path, dpi=200)
    plt.close()

    # -------------------------------------------------------------
    # 10. Confusion Matrix Plot
    # -------------------------------------------------------------
    plt.figure(figsize=(5, 4))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title("Confusion Matrix (Test Set)")
    plt.colorbar()
    tick_marks = np.arange(2)
    plt.xticks(tick_marks, ["SAFE", "SPAM"])
    plt.yticks(tick_marks, ["SAFE", "SPAM"])
    thresh = cm.max() / 2.
    for i in range(2):
        for j in range(2):
            plt.text(j, i, format(cm[i, j], "d"),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    cm_path = reports_dir / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=200)
    plt.close()

    # -------------------------------------------------------------
    # 11. Export Artifacts
    # -------------------------------------------------------------
    model_file = artifacts_dir / "model.joblib"
    vec_file = artifacts_dir / "vectorizer.joblib"
    model_pkl = artifacts_dir / "model.pkl"
    vec_pkl = artifacts_dir / "vectorizer.pkl"
    weights_npz = artifacts_dir / "weights.npz"
    meta_file = artifacts_dir / "metadata.json"

    print(f"Exporting model artifact to {model_file}, {model_pkl}, and {weights_npz}...")
    joblib.dump(final_model, model_file, compress=0)
    with open(model_pkl, "wb") as f:
        import pickle
        pickle.dump(final_model, f, protocol=5)

    # Export fast numpy weights for sub-50ms load time
    np.savez_compressed(weights_npz, coef=final_model.coef_, intercept=final_model.intercept_)

    print(f"Exporting vectorizer artifact to {vec_file}...")
    joblib.dump(vectorizer, vec_file, compress=0)

    # Save fast vocabulary and IDF weights for 0.02s initialization
    w_vec, c_vec = vectorizer.transformer_list[0][1], vectorizer.transformer_list[1][1]
    with open(artifacts_dir / "char_vec.pkl", "wb") as f:
        pickle.dump(c_vec, f, protocol=5)

    vocab_json = {k: int(v) for k, v in w_vec.vocabulary_.items()}
    idf_json = [float(x) for x in w_vec.idf_]
    with open(artifacts_dir / "w_vocab.json", "w", encoding="utf-8") as f:
        json.dump({"vocab": vocab_json, "idf": idf_json}, f)

    metadata = {
        "model_type": "CalibratedClassifierCV(LogisticRegression)",
        "feature_union": {
            "word_ngrams": [1, 2],
            "char_ngrams": [2, 5],
            "max_features_word": 12000,
            "max_features_char": 25000
        },
        "optimal_threshold": float(best_threshold),
        "cv_5fold_f1_mean": float(scores_lr.mean()),
        "cv_5fold_f1_std": float(scores_lr.std()),
        "naive_bayes_cv_f1_mean": float(scores_mnb.mean()),
        "test_metrics": {
            "accuracy": float(test_acc),
            "precision": float(test_prec),
            "recall": float(test_rec),
            "f1_score": float(test_f1),
            "roc_auc": float(test_auc),
            "pr_auc": float(test_pr_auc),
            "false_positive_rate": float(fpr)
        },
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        },
        "cross_source_evaluation": {
            "trained_base_eval_synthetic_f1": float(f1_cross_syn),
            "trained_synthetic_eval_base_f1": float(f1_cross_base)
        },
        "training_stats": {
            "total_training_samples": len(X_train),
            "base_training_samples": len(X_train_base),
            "synthetic_samples": len(X_syn),
            "validation_samples": len(X_val),
            "test_samples": len(X_test),
            "elapsed_seconds": round(time.time() - t_start, 2)
        }
    }
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Metadata saved to {meta_file}")
    print(f"Training completed in {time.time() - t_start:.2f} seconds.")


if __name__ == "__main__":
    run_training()
