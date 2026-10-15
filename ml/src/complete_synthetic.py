import random
from pathlib import Path
import pandas as pd

p = Path("ml/data/synthetic_sms.csv")
df = pd.read_csv(p)
existing_texts = set(df["text"].str.strip().str.lower())

more_records = []

# Casual Hinglish chat variations
names = ["Bhai", "Yaar", "Bro", "Rohit", "Vikram", "Sneha", "Rahul", "Pooja", "Aman"]
activities = [
    "gym chalna hai kya?", "chai peene chale?", "badminton court book kar diya hai",
    "kal ka match dekhne aayega?", "notes bhej de please", "laptop ka charger le aana",
    "shaam ko market chalna hai kya?", "biryani order karein?", "metro station pahunch gaya hoon",
    "kal office kitne baje aayega?", "movie ke tickets book kar doon?", "shaam ko CCD mein milte hain"
]
times = ["5 baje", "6:30 baje", "kal subah 8 baje", "aaj dopehar mein", "shaam ko 7 baje", "10 minute mein"]

hinglish_count = sum(1 for _, r in df.iterrows() if r.get("category") == "casual_hinglish_chat")
needed_hinglish = 75 - hinglish_count
for n in names:
    for a in activities:
        for t in times:
            if len([r for r in more_records if r["category"] == "casual_hinglish_chat"]) >= needed_hinglish:
                break
            text = f"{n}, {t} {a}?"
            if text.lower() not in existing_texts:
                more_records.append({"text": text, "label": "SAFE", "category": "casual_hinglish_chat", "source": "synthetic"})
                existing_texts.add(text.lower())

# Casual English chat variations
eng_phrases = [
    "Are you available for a quick sync at 3 PM?", "Did you get a chance to review the document?",
    "Lunch is arriving in 15 minutes, meet in the cafeteria.", "Please share the presentation link before the call.",
    "Can you review the PR when you get a moment?", "Heading to the coffee machine, want anything?",
    "Great work on today's sprint demo!", "I will be working remotely tomorrow due to internet maintenance.",
    "Let me know once you push the latest changes to staging.", "Happy Birthday! Have a wonderful day ahead."
]
colleagues = ["Alex", "Sarah", "David", "Priya", "John", "Emma", "Michael", "Neha"]
eng_count = sum(1 for _, r in df.iterrows() if r.get("category") == "casual_english_chat")
needed_eng = 75 - eng_count
for c in colleagues:
    for ep in eng_phrases:
        if len([r for r in more_records if r["category"] == "casual_english_chat"]) >= needed_eng:
            break
        text = f"Hi {c}, {ep}"
        if text.lower() not in existing_texts:
            more_records.append({"text": text, "label": "SAFE", "category": "casual_english_chat", "source": "synthetic"})
            existing_texts.add(text.lower())

# Scam warnings educational variations
banks = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Bank", "Punjab National Bank", "RBI", "TRAI", "Cyber Police"]
scam_types = ["lottery prize", "electricity disconnection", "KYC update", "part-time job offer", "unpaid challan", "customs courier fee"]
actions = ["Never share your OTP or UPI PIN", "Do not click on links from unknown numbers", "Bank never calls asking for CVV or password", "Report fraud immediately to 1930"]

warn_count = sum(1 for _, r in df.iterrows() if r.get("category") == "scam_warning_educational")
needed_warn = 75 - warn_count
for b in banks:
    for st in scam_types:
        for ac in actions:
            if len([r for r in more_records if r["category"] == "scam_warning_educational"]) >= needed_warn:
                break
            text = f"Security Advisory from {b}: Beware of fraudulent messages promising {st}. {ac}."
            if text.lower() not in existing_texts:
                more_records.append({"text": text, "label": "SAFE", "category": "scam_warning_educational", "source": "synthetic"})
                existing_texts.add(text.lower())

# Brand promo variations
brands = ["Domino's Pizza", "Swiggy", "Zomato", "Amazon", "Flipkart", "Myntra", "BookMyShow", "Tata 1mg", "Zepto"]
offers = ["Flat 40% OFF on all orders today", "Buy 1 Get 1 Free on medium sizes", "Weekend flash sale is now live", "Enjoy free delivery on orders above Rs 199", "Extra 10% instant discount with HDFC cards"]
promo_count = sum(1 for _, r in df.iterrows() if r.get("category") == "legitimate_brand_promotional")
needed_promo = 75 - promo_count
for br in brands:
    for off in offers:
        if len([r for r in more_records if r["category"] == "legitimate_brand_promotional"]) >= needed_promo:
            break
        text = f"{br}: {off}! Order on official app or verify at official website."
        if text.lower() not in existing_texts:
            more_records.append({"text": text, "label": "SAFE", "category": "legitimate_brand_promotional", "source": "synthetic"})
            existing_texts.add(text.lower())

if more_records:
    df_more = pd.DataFrame(more_records)
    df_all = pd.concat([df, df_more], ignore_index=True)
    df_all.to_csv(p, index=False)
    print(f"Added {len(more_records)} items. Total now: {len(df_all)}")
    print(df_all["label"].value_counts())
else:
    print(f"Already satisfied! Total: {len(df)}")
