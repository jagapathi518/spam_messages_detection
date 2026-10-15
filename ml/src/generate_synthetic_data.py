"""Generate synthetic Indian/Hinglish SMS and chat messages via Groq API + Generative Variations.
Targets ~1,500 diverse messages (balanced between SPAM and SAFE, 75 per category * 20 = 1,500), covering:
- KYC, UPI, Challan, Bank, Electricity, Courier, Lottery, Job, Loan scams, Obfuscated spam.
- Real transactional alerts, genuine OTPs, delivery updates, recharges, appointments,
  casual Hinglish chats, and scam awareness warnings.

Marked source="synthetic" for TRAINING ONLY.
"""
import os
import json
import time
import random
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import pandas as pd

# Load environment
env_path = Path(__file__).resolve().parent.parent.parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment or backend/.env")

client = Groq(api_key=api_key)
MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

CATEGORIES_SPAM = [
    ("sbi_hdfc_kyc_scam", "SBI/HDFC/ICICI bank account blocked today, update pan/kyc at shortlink/apk"),
    ("upi_cashback_scam", "PhonePe/GPay scratch card win Rs 1999 or cashback refund link"),
    ("traffic_challan_scam", "Traffic police pending e-challan notice, court warrant, download echallan.apk"),
    ("electricity_bill_scam", "Bijli disconnection tonight at 9:30 PM due to unpaid bill, contact officer immediately"),
    ("courier_parcel_scam", "India Post / FedEx parcel detained due to invalid address, update within 12h"),
    ("lottery_kbc_scam", "KBC Jio lucky winner 25 lakh lottery, contact WhatsApp manager"),
    ("wfh_part_time_job_scam", "Earn 2000-5000 daily by liking YouTube videos or review rating, message HR on Telegram"),
    ("instant_loan_scam", "Instant personal loan Rs 5,00,000 approved at 0% interest, download quickloan.apk"),
    ("obfuscated_spam", "L0an appr0ved, cl!ck here fr33 c@sh, urg3nt off3r, w.h.a.t.s.a.p.p me"),
    ("brand_lookalike_promo", "Fake Zara/Myntra/Apple 90% discount sale flash clearance at suspicious .xyz/.site domain")
]

CATEGORIES_SAFE = [
    ("bank_debit_credit_alert", "Realistic bank SMS: A/c *1234 debited INR 850 at Swiggy, UPI Ref 4123..., Avl Bal INR 12,450"),
    ("genuine_otp_message", "123456 is your secret OTP for login to Zomato/Amazon. Do not share with anyone including bank officials."),
    ("delivery_status_update", "Your order #98721 from Flipkart is out for delivery today with wishmaster Rahul. Pin: 44"),
    ("mobile_recharge_confirmation", "Recharge of Rs 299 successful on your Airtel/Jio number 98XXXX1234. 1.5GB/day valid for 28 days."),
    ("service_appointment_reminder", "Reminder: Your dental appointment with Dr. Sharma is scheduled for tomorrow at 4:00 PM at Apollo Clinic."),
    ("casual_hinglish_chat", "Bhai shaam ko CCD mein milte hain. Laptop leke aana project discuss karenge."),
    ("casual_english_chat", "Hey, are you joining the team lunch today? We are heading out in 15 mins."),
    ("scam_warning_educational", "ALERT: SBI never asks for OTP, PIN or CVV. Do not click on unknown links claiming KYC update. Stay safe."),
    ("legit_travel_pnr", "IRCTC PNR 4521367890: Train 12952 Confirmed B3 42 MB. Charting done. Happy journey."),
    ("legitimate_brand_promotional", "Domino's Pizza: Buy 1 Get 1 Free on all Medium Pizzas today only! Order on official Domino's App or dominos.co.in")
]

TEMPLATES_SPAM = {
    "sbi_hdfc_kyc_scam": [
        "Dear {bank} User, your account is temporarily restricted. Complete your PAN verification at http://{slug}-portal.{tld}/kyc immediately.",
        "URGENT {bank} Notice: Your NetBanking service will expire today. Update KYC documents online: http://{slug}-verify.{tld}/auth",
        "{bank} Alert: Account #{acc} blocked due to unlinked Aadhaar. Download {bank}_Update.apk from http://{slug}-app.{tld}",
        "Dear customer, your {bank} YONO account is locked. Update KYC to continue debit card services: http://{slug}-online.{tld}",
        "Attention: {bank} card disabled. Re-verify KYC within 24h at http://{slug}-service.{tld} or visit branch.",
        "Final warning from {bank}: Submit PAN details at http://{slug}-desk.{tld} to unfreeze account {acc}."
    ],
    "upi_cashback_scam": [
        "Congratulations! You won Rs {amt} cashback in {wallet}. Scratch card waiting, claim to bank: http://{slug}-rewards.{tld}",
        "{wallet} Offer: Rs {amt} festival refund sent to your UPI ID. Enter UPI PIN to approve transfer: http://{slug}-refund.{tld}",
        "Instant Cash Reward! Rs {amt} credited to your {wallet} wallet. Click http://{slug}-claim.{tld} to withdraw to SBI/HDFC.",
        "You received Rs {amt} bonus from {wallet} Diwali Dhamaka! Tap to collect money directly: http://{slug}-payout.{tld}",
        "Special Gift: Rs {amt} cash voucher pending in your {wallet} app. Redeem at http://{slug}-redeem.{tld}"
    ],
    "traffic_challan_scam": [
        "Traffic Police: Notice for pending traffic violation challan Rs {amt} on vehicle {reg}. Pay now to avoid court: http://echallan-{slug}.{tld}",
        "E-Challan Alert: Speed violation caught on camera for {reg}. Download Parivahan_Challan.apk from http://parivahan-{slug}.{tld}",
        "Notice: Pending court challan for {reg}. Settle fine Rs {amt} before warrant issue at http://challan-pay-{slug}.{tld}",
        "State Police: E-challan #{acc} unpaid for 60 days on {reg}. Resolve immediately at http://traffic-settle-{slug}.{tld}"
    ],
    "electricity_bill_scam": [
        "Dear Consumer, power supply to meter {acc} will be disconnected tonight at {hour}:30 PM due to unpaid bill. Call officer {phone} now.",
        "Electricity Department Alert: Disconnection order issued for unpaid bill Rs {amt}. Contact divisional officer at {phone} immediately.",
        "Bijli Office Notice: Tonight 9:30 PM line will be cut off for CA #{acc}. Contact power executive on {phone} urgently.",
        "Power Department: Immediate notice of disconnection for consumer #{acc}. Verify payment on {phone} to prevent disruption."
    ],
    "courier_parcel_scam": [
        "India Post: Your package #{track} is held at regional depot due to wrong pin code. Update address in 12h: http://indiapost-{slug}.{tld}",
        "BlueDart Courier: Consignment #{track} delivery failed. Confirm address & pay Rs 5 re-delivery fee at http://bluedart-{slug}.{tld}",
        "Delhivery Notice: Parcel #{track} pending customs clearance. Update details at http://delhivery-{slug}.{tld}",
        "DTDC Express: Urgent! Address missing for package #{track}. Re-schedule delivery at http://dtdc-{slug}.{tld}"
    ],
    "lottery_kbc_scam": [
        "Dear customer, you won Rs {amt}0,000 in KBC Jio Lucky Draw 2026. Contact WhatsApp manager on {phone} to receive cheque.",
        "Special Winner: Mobile #{phone} selected for free Apple iPhone 16 Pro! Claim today: http://lucky-draw-{slug}.{tld}",
        "Congratulations! Your SIM number won 2nd prize of Rs 15 Lakhs in Golden Bumper draw. WhatsApp {phone} to claim.",
        "Dubai Shopping Festival: Ticket #{acc} selected for cash prize of USD 10,000. Send details to manager on {phone}."
    ],
    "wfh_part_time_job_scam": [
        "Work from Home! Earn Rs {amt} daily by liking YouTube videos and rating hotels on Google. WhatsApp HR on {phone}.",
        "Amazon Part-Time Hiring: Daily 1 hour work, earn Rs {amt} per task via UPI. Join official Telegram channel @amazon_wfh_{slug}",
        "Mobile Job Opportunity: Watch movie trailers and get Rs {amt} daily directly into bank. Message HR on Telegram @hiring_desk_{slug}",
        "Daily Earning: Earn Rs 250 per review rating. Immediate payout via GPay/PhonePe. Join Telegram @job_portal_{slug}"
    ],
    "instant_loan_scam": [
        "Pre-approved loan Rs {amt}0,000 sanctioned for your PAN card at 1% interest. Zero CIBIL check. Disbursal in 5m: http://quick-loan-{slug}.{tld}",
        "Need instant cash? Rs {amt}0,000 approved on Aadhaar card. Install PaisaLoan.apk from http://fast-loan-{slug}.{tld}",
        "Instant Credit: Rs {amt}0,000 ready for withdrawal. No salary slip needed. Complete e-sign at http://credit-now-{slug}.{tld}",
        "Govt Mudra Subsidy: Loan of Rs 3,00,000 pre-approved at 0% fees. Download APK at http://mudra-loan-{slug}.{tld}"
    ],
    "obfuscated_spam": [
        "U.r.g.e.n.t: Y0ur {bank} b@nk @cct is bl0cked! Cl!ck http://{slug}-kyc.{tld} t0 upd@te k.y.c.",
        "C.o.n.g.r.a.t.s! U w0n Rs {amt}00 c@sh! Wh@ts@pp {phone} t0 cl@im n0w.",
        "Fr33 l0an @ppr0ved Rs {amt}0,000! C1ick http://l-o-a-n-{slug}.{tld} imm3diately.",
        "E.l.e.c.t.r.i.c.i.t.y cut off t0night! C@ll 0fficer on {phone} t0 st0p disconn3ct.",
        "P.h.o.n.e.P.e c@shb@ck Rs {amt} w@iting for u. Cl!ck http://tinyurl.com/{slug} t0 tr@nsfer."
    ],
    "brand_lookalike_promo": [
        "Zara Clearance Sale: Flat 90% OFF on all luxury collection today only! Order at http://zara-store-{slug}.{tld}",
        "Apple Mega Sale: Factory refurbished iPhone at Rs 12,999! Limited stock: http://apple-offers-{slug}.{tld}",
        "Nike Warehouse Sale: Sneakers starting at Rs 799! Free delivery on http://nike-outlet-{slug}.{tld}",
        "Tanishq Gold Offer: Flat 50% off on making charges today only! Book coupon: http://tanishq-deals-{slug}.{tld}"
    ]
}

TEMPLATES_SAFE = {
    "bank_debit_credit_alert": [
        "Dear Customer, your {bank} A/c XX{acc} is debited by INR {amt}.00 on 15-Oct-26 at Swiggy/Zomato. Avl Bal: INR {amt}40.00. - {bank}",
        "{bank} Alert: INR {amt}0.00 credited to A/c ending {acc} by NEFT on 15-Oct-26. Total Balance: INR {amt}50.00.",
        "{bank}: INR {amt}.00 debited from card XX{acc} at Indian Oil Pump. Avl Limit: INR 85,000.00. If not you, SMS BLOCK to 567676.",
        "Your {bank} A/c XX{acc} has been credited with salary INR {amt}0.00 on 15-OCT-26. Clear Bal: INR {amt}80.00."
    ],
    "genuine_otp_message": [
        "{otp} is your secret OTP for login to {brand}. Valid for 5 minutes. Do NOT share this OTP with anyone.",
        "Your verification code for {brand} is {otp}. Never share this code with anyone including support executives.",
        "Use OTP {otp} to authenticate your transaction of INR {amt}.00 at {brand}. Bank never calls for OTP.",
        "{otp} is OTP for Aadhaar verification. Valid for 10 mins. UIDAI never asks for OTP."
    ],
    "delivery_status_update": [
        "Your order #{track} from {brand} is out for delivery today with delivery partner {name}. Share OTP {otp_short} on delivery.",
        "Shipment #{track} has arrived at your local hub and will be delivered by 6 PM today via {brand}.",
        "{brand}: Order #{track} containing essentials has been delivered. Thank you for choosing us!",
        "Your package #{track} from {brand} has been dispatched. Track in real time on the official app."
    ],
    "mobile_recharge_confirmation": [
        "Recharge of Rs {recharge_amt} is successful for your {telecom} number 98XXXX{acc}. Plan validity 28 days. Enjoy unlimited 5G data.",
        "{telecom}: Bill payment of Rs {recharge_amt} processed successfully for mobile {acc}. Current outstanding: Rs 0.00.",
        "Thank you! Your pack of Rs {recharge_amt} on {telecom} mobile 98XXXX{acc} is activated. Enjoy high-speed data.",
        "{telecom} confirmation: Payment of Rs {recharge_amt} received. Next recharge due on 18-Nov-2026."
    ],
    "service_appointment_reminder": [
        "Appointment Confirmation: Your consultation with Dr. {doctor} is scheduled for tomorrow at {hour}:00 PM at Apollo Clinic.",
        "Reminder: Urban Company home cleaning service is confirmed for tomorrow at {hour}:30 AM. Booking ID: #UC{track}.",
        "Your service appointment for vehicle {reg} is scheduled for tomorrow 10:00 AM at authorized service center.",
        "Practo Reminder: Tele-consultation with Dr. {doctor} starts in 15 minutes. Join via Practo app."
    ],
    "casual_hinglish_chat": [
        "Bhai shaam ko kahan chalna hai? 6 baje CCD mein milte hain ya cafe chalenge?",
        "Arey sun kal ka assignment submit ho gaya kya? Mujhe bhi uska code bhej de na.",
        "Bhai main 10 minute mein pahunch raha hoon, order de dena tab tak.",
        "Kal ka movie plan confirm hai? Main tickets book kar doon kya BookMyShow par?",
        "Mummy boli market se aate hue sabzi lete aana please.",
        "Weekend par cricket match khelte hain ground par. Batting teri pehle hogi."
    ],
    "casual_english_chat": [
        "Hey, are you free for a quick call regarding the project architecture?",
        "Thanks for sharing the meeting notes, I will review and update the deck today.",
        "Did you get a chance to test the latest API build? Let me know if everything looks good.",
        "Are you joining the lunch today? We are heading out to the food court in 10 minutes.",
        "Happy Birthday! Wishing you a fantastic year ahead with great achievements."
    ],
    "scam_warning_educational": [
        "Warning from {bank}: Never share your OTP, UPI PIN, or Password with anyone. Bank never calls asking for confidential details.",
        "Alert: Beware of fake SMS threatening electricity disconnection or KYC block. Never call unknown phone numbers or install APKs.",
        "Advisory: Do not enter your UPI PIN to receive money. UPI PIN is required ONLY to pay or transfer money.",
        "Cyber Security Alert: TRAI never blocks mobile numbers via SMS. Report suspicious scam texts to 1930."
    ],
    "legit_travel_pnr": [
        "IRCTC PNR {pnr}: Train {train} Confirmed Coach B{coach} Seat {seat}. Chart prepared. Have a safe journey.",
        "IndiGo Flight #{pnr}: Web check-in open for flight 6E-{train} departing tomorrow at {hour}:15 hrs. Gate details on boarding pass.",
        "MakeMyTrip Booking Confirmed: Hotel Grand Stay, 2 Nights. Check-in tomorrow at 12:00 PM. Booking ID: MMT{acc}.",
        "RedBus: Your bus from Bangalore to Hyderabad departs tonight at 10:30 PM from Madiwala. Bus No: KA01F{acc}."
    ],
    "legitimate_brand_promotional": [
        "Domino's Pizza: Flat 40% OFF on all Gourmet Pizzas! Use code PIZZA40 on official Domino's App or https://dominos.co.in",
        "Amazon India: Great Indian Festival deals live! Extra 10% instant discount on official Amazon app https://amazon.in",
        "Flipkart: Big Billion Days specials live today on verified app and https://flipkart.com",
        "Swiggy: Weekend cravings? Enjoy flat Rs 100 off on top rated restaurants with code TASTY100 on Swiggy app."
    ]
}


def fill_template(tmpl: str) -> str:
    banks = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Bank", "PNB", "Bank of Baroda", "Canara Bank", "Union Bank", "IndusInd Bank"]
    wallets = ["PhonePe", "Google Pay", "Paytm", "BHIM UPI", "Cred"]
    tlds = ["xyz", "top", "site", "icu", "click", "online", "club", "info"]
    brands = ["Amazon", "Flipkart", "Swiggy", "Zomato", "Myntra", "Zepto", "Blinkit", "BigBasket", "Uber", "Ola"]
    telecoms = ["Jio", "Airtel", "Vi", "BSNL"]
    doctors = ["Sharma", "Verma", "Rao", "Gupta", "Mehta", "Patel", "Reddy", "Nair", "Iyer", "Chopra"]
    names = ["Rahul", "Sunil", "Vikram", "Amit", "Deepak", "Ramesh", "Priya", "Ananya", "Rohit", "Suresh"]

    return tmpl.format(
        bank=random.choice(banks),
        wallet=random.choice(wallets),
        tld=random.choice(tlds),
        slug=f"portal{random.randint(100, 9999)}",
        acc=f"{random.randint(1000, 9999)}",
        amt=f"{random.randint(5, 95) * 100}",
        phone=f"+91{random.randint(7000000000, 9999999999)}",
        hour=f"{random.randint(8, 11)}",
        reg=f"MH0{random.randint(1,4)}AB{random.randint(1000, 9999)}",
        track=f"{random.randint(10000000, 99999999)}",
        otp=f"{random.randint(100000, 999999)}",
        otp_short=f"{random.randint(10, 99)}",
        brand=random.choice(brands),
        telecom=random.choice(telecoms),
        recharge_amt=random.choice([299, 479, 666, 719, 839, 999]),
        doctor=random.choice(doctors),
        name=random.choice(names),
        pnr=f"{random.randint(1000000000, 9999999999)}",
        train=f"{random.randint(12001, 12999)}",
        coach=f"{random.randint(1, 6)}",
        seat=f"{random.randint(1, 64)}"
    )


def generate_batch_groq(category_name: str, prompt_hint: str, label: str, count: int = 5) -> list:
    system_prompt = (
        "You are an assistant specialized in generating synthetic telecom text datasets. "
        "Strict rules: Return ONLY valid JSON with a single key 'messages' containing an array of strings. "
        "Each string must be a SHORT mobile SMS or chat message (10-30 words max, no emails)."
    )
    user_prompt = (
        f"Generate {count} distinct mobile SMS messages in India for category: '{category_name}'. "
        f"Context: {prompt_hint}. "
        f"Ground truth label: {label}. "
        "Return JSON object: {\"messages\": [\"msg1\", \"msg2\", ...]}"
    )

    try:
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=MODEL,
            response_format={"type": "json_object"},
            temperature=0.85,
            max_tokens=250
        )
        content = resp.choices[0].message.content
        parsed = json.loads(content)
        for v in parsed.values():
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], str):
                return v
    except Exception as e:
        print(f"Groq API note: {e}", flush=True)
    return []


def main():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    out_csv = data_dir / "synthetic_sms.csv"

    records = []
    if out_csv.exists():
        existing_df = pd.read_csv(out_csv)
        records = existing_df.to_dict("records")
        print(f"Loaded {len(records)} existing synthetic records from {out_csv}", flush=True)

    current_texts = {r["text"].strip().lower() for r in records}

    # Target: 75 per category * 10 = 750 SPAM, and 75 per category * 10 = 750 SAFE -> 1,500 total
    print("\n--- Processing Synthetic SPAM Categories ---", flush=True)
    for cat_name, hint in CATEGORIES_SPAM:
        existing_cat = sum(1 for r in records if r.get("category") == cat_name)
        needed = 75 - existing_cat
        if needed <= 0:
            print(f"[SPAM] {cat_name}: already has {existing_cat} items.", flush=True)
            continue
        print(f"[SPAM] {cat_name}: generating {needed} items...", flush=True)

        # 1. Groq generation (micro-batch of 5 to respect TPM)
        msgs = generate_batch_groq(cat_name, hint, "SPAM", count=5)
        for m in msgs:
            m_clean = m.strip()
            if m_clean and len(m_clean) > 8 and m_clean.lower() not in current_texts:
                records.append({
                    "text": m_clean,
                    "label": "SPAM",
                    "category": cat_name,
                    "source": "synthetic"
                })
                current_texts.add(m_clean.lower())

        # 2. Template augmentation up to 75
        existing_cat_now = sum(1 for r in records if r.get("category") == cat_name)
        shortfall = 75 - existing_cat_now
        if shortfall > 0 and cat_name in TEMPLATES_SPAM:
            tmpls = TEMPLATES_SPAM[cat_name]
            attempts = 0
            while sum(1 for r in records if r.get("category") == cat_name) < 75 and attempts < shortfall * 5:
                attempts += 1
                syn_msg = fill_template(random.choice(tmpls))
                if syn_msg.lower() not in current_texts:
                    records.append({
                        "text": syn_msg,
                        "label": "SPAM",
                        "category": cat_name,
                        "source": "synthetic"
                    })
                    current_texts.add(syn_msg.lower())

        print(f"[SPAM] {cat_name}: count is now {sum(1 for r in records if r.get('category') == cat_name)}. Total records: {len(records)}", flush=True)
        pd.DataFrame(records).to_csv(out_csv, index=False)

    print("\n--- Processing Synthetic SAFE Categories ---", flush=True)
    for cat_name, hint in CATEGORIES_SAFE:
        existing_cat = sum(1 for r in records if r.get("category") == cat_name)
        needed = 75 - existing_cat
        if needed <= 0:
            print(f"[SAFE] {cat_name}: already has {existing_cat} items.", flush=True)
            continue
        print(f"[SAFE] {cat_name}: generating {needed} items...", flush=True)

        # 1. Groq generation (micro-batch of 5)
        msgs = generate_batch_groq(cat_name, hint, "SAFE", count=5)
        for m in msgs:
            m_clean = m.strip()
            if m_clean and len(m_clean) > 8 and m_clean.lower() not in current_texts:
                records.append({
                    "text": m_clean,
                    "label": "SAFE",
                    "category": cat_name,
                    "source": "synthetic"
                })
                current_texts.add(m_clean.lower())

        # 2. Template augmentation up to 75
        existing_cat_now = sum(1 for r in records if r.get("category") == cat_name)
        shortfall = 75 - existing_cat_now
        if shortfall > 0 and cat_name in TEMPLATES_SAFE:
            tmpls = TEMPLATES_SAFE[cat_name]
            attempts = 0
            while sum(1 for r in records if r.get("category") == cat_name) < 75 and attempts < shortfall * 5:
                attempts += 1
                syn_msg = fill_template(random.choice(tmpls))
                if syn_msg.lower() not in current_texts:
                    records.append({
                        "text": syn_msg,
                        "label": "SAFE",
                        "category": cat_name,
                        "source": "synthetic"
                    })
                    current_texts.add(syn_msg.lower())

        print(f"[SAFE] {cat_name}: count is now {sum(1 for r in records if r.get('category') == cat_name)}. Total records: {len(records)}", flush=True)
        pd.DataFrame(records).to_csv(out_csv, index=False)

    df = pd.DataFrame(records)
    df.to_csv(out_csv, index=False)
    print(f"\n==========================================", flush=True)
    print(f"COMPLETE! Saved {len(df)} synthetic SMS messages to {out_csv}", flush=True)
    print(f"==========================================", flush=True)
    print(df["label"].value_counts(), flush=True)


if __name__ == "__main__":
    main()
