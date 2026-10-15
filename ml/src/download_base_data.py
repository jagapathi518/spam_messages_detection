"""Download base SMS dataset (UCI Machine Learning SMS Spam Collection).

Ensures only short mobile SMS/chat messages are included. No email datasets.
"""
from pathlib import Path
import urllib.request
import pandas as pd


def fetch_sms_dataset(dest_path: Path) -> Path:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists():
        print(f"Dataset already exists at {dest_path}")
        return dest_path

    url = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
    print(f"Downloading SMS Spam Collection from {url}...")
    urllib.request.urlretrieve(url, dest_path)
    print(f"Downloaded to {dest_path}")
    return dest_path


def load_normalized_base_sms(tsv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(tsv_path, sep="\t", header=None, names=["raw_label", "text"], encoding="utf-8")
    # Clean and map
    df["label"] = df["raw_label"].map({"ham": "SAFE", "spam": "SPAM"})
    df["source"] = "uci_sms_collection"
    df["text"] = df["text"].astype(str).str.strip()
    # Filter short messages (< 600 chars typical for SMS/chats)
    df = df[df["text"].str.len() > 2]
    df = df[df["text"].str.len() < 800]
    df = df[["text", "label", "source"]].drop_duplicates(subset=["text"])
    return df


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent / "data"
    raw_file = base_dir / "sms_raw.tsv"
    fetch_sms_dataset(raw_file)
    df = load_normalized_base_sms(raw_file)
    output_file = base_dir / "base_sms_clean.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} cleaned base SMS messages to {output_file}")
    print(df["label"].value_counts())
