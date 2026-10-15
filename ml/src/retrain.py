"""Continuous Learning Retraining Script for Spam Shield.

Fetches user-submitted false positive and false negative reports from Supabase,
merges confirmed feedback with existing training data, deduplicates,
and retrains the calibrated model artifacts.
"""
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from supabase import create_client, Client

# Add parent directory to path
repo_root = Path(__file__).resolve().parent.parent.parent
env_path = repo_root / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

from ml.src.train import run_training, deduplicate_dataset


def fetch_supabase_feedback() -> pd.DataFrame:
    """Fetches user feedback reports from Supabase table 'user_feedback'."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")

    if not url or not key:
        print("Supabase credentials not configured in backend/.env. Skipping remote feedback fetch.")
        return pd.DataFrame()

    try:
        supabase: Client = create_client(url, key)
        resp = supabase.table("user_feedback").select("*").eq("is_verified", True).execute()
        if resp.data and len(resp.data) > 0:
            records = []
            for item in resp.data:
                # user_correction: 'SPAM' or 'SAFE'
                correction = item.get("user_correction") or item.get("correct_label")
                text = item.get("text", "").strip()
                if text and correction in ["SPAM", "SAFE"]:
                    records.append({
                        "text": text,
                        "label": correction,
                        "source": "supabase_feedback"
                    })
            df_fb = pd.DataFrame(records)
            print(f"Fetched {len(df_fb)} verified feedback samples from Supabase.")
            return df_fb
    except Exception as e:
        print(f"Notice: Could not fetch from Supabase (offline or table not initialized yet): {e}")

    return pd.DataFrame()


def retrain_with_feedback():
    data_dir = repo_root / "ml" / "data"
    syn_path = data_dir / "synthetic_sms.csv"

    print("Checking for incoming user feedback...")
    df_feedback = fetch_supabase_feedback()

    if not df_feedback.empty:
        # Load existing synthetic/augmented training file
        df_syn = pd.read_csv(syn_path)
        combined = pd.concat([df_syn, df_feedback], ignore_index=True)
        deduped = deduplicate_dataset(combined)
        deduped.to_csv(syn_path, index=False)
        print(f"Merged feedback into {syn_path}. New total training augmentation: {len(deduped)}")
    else:
        print("No new external feedback to merge. Retraining on current vetted dataset.")

    # Re-run full training and evaluation cycle
    run_training()
    print("Retraining pipeline completed successfully.")


if __name__ == "__main__":
    retrain_with_feedback()
