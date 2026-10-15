"""Layer 1: Rules Engine for Mobile Short Text Message Detection.

Strictly mobile SMS / chat messages. No email terminology or features.
Outputs:
- risk_score: float in [0.0, 1.0]
- reasons: List[str]
- is_exempt_safe: bool (True if transactional / scam warning / legit domain)
- rule_label: "SPAM" | "SUSPICIOUS" | "SAFE"
"""
import re
from typing import List, Tuple, Dict, Any
from urllib.parse import urlparse

# Well-known legitimate domains (never flag as spam merely for having these links)
LEGIT_DOMAINS = {
    "amazon.in", "amazon.com", "flipkart.com", "swiggy.com", "zomato.com",
    "irctc.co.in", "sbi.co.in", "onlinesbi.sbi", "hdfcbank.com", "icicibank.com",
    "axisbank.com", "kotak.com", "bankofbaroda.in", "pnbindia.in", "canarabank.com",
    "parivahan.gov.in", "echallan.parivahan.gov.in", "uidai.gov.in", "incometax.gov.in",
    "myntra.com", "bookmyshow.com", "paytm.com", "phonepe.com", "google.com",
    "dominos.co.in", "zepto.com", "blinkit.com", "tataplay.com", "airtel.in",
    "jio.com", "myvi.in", "uber.com", "olacabs.com", "cult.fit", "practo.com",
    "delhivery.com", "bluedart.com", "indiapost.gov.in"
}

# Suspicious TLDs frequently used in mobile phishing
SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".click", ".icu", ".site", ".club", ".online", ".link",
    ".cfd", ".buzz", ".monster", ".work", ".rest", ".info", ".live"
}

# Known URL shorteners
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "tiny.cc", "is.gd", "buff.ly", "ow.ly",
    "t.co", "goo.gl", "bit.do", "cutt.ly", "shorturl.at", "rb.gy"
}

# Bank & Payment brand tokens targeted by lookalikes
BRAND_TOKENS = [
    "sbi", "yono", "hdfc", "icici", "axis", "kotak", "pnb", "bob", "canara",
    "paytm", "phonepe", "gpay", "bhim", "cred", "parivahan", "echallan",
    "indiapost", "bluedart", "delhivery", "bses", "msedcl", "dhbvn", "apple", "zara", "nike"
]

SUSPICIOUS_URL_SLUGS = [
    "kyc", "pan", "login", "verify", "update", "unblock", "refund", "claim",
    "reward", "bonus", "cashback", "apk", "challan", "disbursal", "gift", "payout"
]


class RulesEngine:
    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        # 1. Scam Warning patterns (Context Rule B)
        self.scam_warning_regex = re.compile(
            r"\b(never\s+share\s+(?:your\s+)?(?:otp|pin|password|cvv)|"
            r"bank\s+never\s+(?:calls|asks|sends\s+sms)|"
            r"(?:it\s*'?s|this\s+is)\s+a\s+scam|"
            r"beware\s+of\s+(?:fake|fraud|scam)|"
            r"(?:delhi\s+police|cyber\s+dost|cyber\s+crime|police)\s+advisory|"
            r"rbi\s+kehta\s+hai|"
            r"trai\s+never\s+disconnects|"
            r"warning:\s*(?:do\s+not\s+(?:accept|enter|share|click)|beware)|"
            r"security\s+(?:warning|tip|advisory)|"
            r"do\s+not\s+(?:click|share|call|transfer)\s+.*(?:scam|fraud|unknown)|"
            r"report\s+(?:fraud|unauthorized)\s+(?:to\s+)?1930)\b",
            re.IGNORECASE
        )

        # 2. Genuine Transactional patterns (Context Rule A)
        self.bank_alert_regex = re.compile(
            r"\b(?:a/c\s*(?:no\.?|ending)?\s*(?:xx|\.\.\.|\*)\d+|\b(?:debited|credited)\s+by\s+(?:inr|rs\.?)|"
            r"\b(?:inr|rs\.?)\s*[\d,]+(?:\.\d{2})?\s+(?:debited|credited|transferred|received)|"
            r"avl\s*(?:bal|balance)|net\s*available\s*balance|clear\s*bal|"
            r"zero\s+balance\s+savings\s+account|"
            r"credit\s+card\s+(?:xx|\*)\d+\s+charged|atm\s+cash\s+withdrawal|"
            r"upi\s+(?:ref|txn)\s*(?:no\.?|id)?\s*[\w\d]{8,})\b",
            re.IGNORECASE
        )

        self.otp_regex = re.compile(
            r"\b(?:\b\d{4,8}\s+(?:is\s+(?:your\s+)?(?:secret\s+)?(?:one\s+time\s+password|otp|verification\s+code))|"
            r"(?:otp|verification\s+code)\s*(?:is|for)?\s*:?\s*\b\d{4,8}\b|"
            r"use\s+(?:code|otp)\s+\d{4,8}\b|"
            r"valid\s+for\s+\d+\s+min(?:ute)?s?\b)\b",
            re.IGNORECASE
        )

        self.delivery_regex = re.compile(
            r"\b(?:out\s+for\s+delivery|order\s*#?\s*\d+[\w-]*\s+is\s+arriving|"
            r"waybill\s*#?\s*\d+|is\s+arriving\s+today|"
            r"delivery\s+(?:associate|partner|wishmaster)|pnr\s*\d{10}\b|"
            r"fastag\s+recharge|plan\s+(?:validity\s+\d+\s+days|renewal\s+successful)|"
            r"recharge\s+of\s+rs\.?\s*\d+\s+(?:successful|received)|"
            r"payment\s+of\s+(?:rs\.?|inr)\s*\d+[\d,.]*\s+received|"
            r"postpaid\s+bill|subscriber\s+id\s*\d+|"
            r"due\s+for\s+(?:\d+(?:st|nd|rd|th)\s+)?(?:free\s+)?service)\b",
            re.IGNORECASE
        )

        # 3. Phishing / Scam indicator patterns
        self.kyc_scam_regex = re.compile(
            r"\b(?:account\s+(?:will\s+be\s+)?blocked\s+today|"
            r"netbanking\s+(?:access\s+is\s+)?suspended|"
            r"debit\s+card\s+(?:has\s+been\s+)?deactivated|"
            r"(?:update|re-?verify|submit)\s+(?:pan|kyc|aadhaar)\s+immediately|"
            r"yono\s+account\s+is\s+locked|"
            r"to\s+avoid\s+(?:permanent\s+block|account\s+closure))\b",
            re.IGNORECASE
        )

        self.upi_scam_regex = re.compile(
            r"\b(?:received\s+a?\s*cashback\s+reward\s+of|"
            r"won\s+a?\s*scratch\s+card|"
            r"refund\s+of\s+rs\.?\s*[\d,]+\s+is\s+ready|"
            r"enter\s+upi\s+pin\s+to\s+(?:receive|confirm\s+credit|accept)|"
            r"send\s+upi\s+pin\s+to\s+confirm)\b",
            re.IGNORECASE
        )

        self.challan_scam_regex = re.compile(
            r"\b(?:e-?challan\s+notice|pending\s+traffic\s+(?:fine|challan)|"
            r"court\s+warrant|non-bailable\s+warrant|vehicle\s+rc\s+suspension|"
            r"lok\s+adalat\s+notice|parivahan_challan\.apk)\b",
            re.IGNORECASE
        )

        self.utility_scam_regex = re.compile(
            r"\b(?:(?:electricity|power|bijli)\s+(?:connection\s+)?(?:will\s+be\s+|is\s+scheduled\s+for\s+)?(?:disconnected|cut\s+off)\s+tonight|"
            r"power\s+cut\s+scheduled\s+tonight\s+at\s+\d{1,2}(?::\d{2})?\s*(?:pm)?|"
            r"immediately\s+contact\s+(?:our\s+)?(?:electricity|power)\s+officer|"
            r"call\s+(?:power|electricity)?\s*officer)\b",
            re.IGNORECASE
        )

        self.courier_scam_regex = re.compile(
            r"\b(?:parcel\s+(?:#?[\w\d]+\s+)?could\s+not\s+be\s+delivered|"
            r"package\s+(?:on\s+hold|detained\s+by\s+customs)|"
            r"update\s+your\s+details\s+within\s+12h|"
            r"re-?delivery\s+fee\s+of\s+rs\b|"
            r"incomplete\s+street\s+address)\b",
            re.IGNORECASE
        )

        self.lottery_scam_regex = re.compile(
            r"\b(?:won\s+(?:rs\.?|cash\s+bonus\s+(?:of\s+)?(?:rs\.?)?)\s*[\d,]+.*(?:lucky\s+draw|kbc|jio|lottery|mega\s+contest)|"
            r"selected\s+for\s+(?:brand\s+new\s+)?apple\s+iphone|"
            r"tata\s+motors\s+lucky\s+draw|contact\s+whatsapp\s+manager|"
            r"pay\s+\d+\s+processing\s+fee.*to\s+claim|"
            r"international\s+mobile\s+lottery)\b",
            re.IGNORECASE
        )

        self.job_scam_regex = re.compile(
            r"\b(?:earn\s+(?:rs\.?\s*)?\d{3,5}\s*(?:to\s*\d{3,5})?\s*(?:per\s+day|daily)\s+by\s+liking\s+youtube|"
            r"part-?time\s+(?:data\s+typing|wfh|job\s+opportunity)|"
            r"earn\s+extra\s+income\s+from\s+mobile|"
            r"subscribe\s+to\s+merchant\s+channels|contact\s+hr\s+.*on\s+telegram|"
            r"join\s+telegram\s+@[\w\d_]+)\b",
            re.IGNORECASE
        )

        self.loan_scam_regex = re.compile(
            r"\b(?:instant\s+personal\s+loan\s+pre-?approved|"
            r"approved\s+without\s+cibil\s+score|"
            r"pre-?approved\s+loan\s+of\s+inr\s+[\d,]+|"
            r"zero\s+cibil\s+loan|disbursal\s+in\s+5\s*m(?:in)?s?|"
            r"no\s+salary\s+slip,\s*no\s+guarantor)\b",
            re.IGNORECASE
        )

        self.apk_download_regex = re.compile(
            r"\b(?:download|install)\s+[\w\d_-]+\.apk|https?://[^\s]+\.apk\b",
            re.IGNORECASE
        )

    def decode_obfuscation(self, text: str) -> str:
        """Decodes leetspeak and interspersed dots/spaces (e.g. 'fr33', 'cl!ck', 'c.l.a.i.m')."""
        t = text
        # Remove inter-letter dots/spaces e.g. "p.h.o.n.e.p.e" -> "phonepe"
        t_condensed = re.sub(r"(?<=\b\w)[.\s_-]+(?=\w\b)", "", t)
        
        # Leet substitutions
        leet_map = {
            "0": "o", "1": "i", "!": "i", "3": "e", "@": "a",
            "4": "a", "$": "s", "5": "s", "7": "t", "8": "b"
        }
        decoded_chars = [leet_map.get(ch, ch) for ch in t_condensed.lower()]
        return "".join(decoded_chars)

    def extract_urls(self, text: str) -> List[str]:
        raw_urls = re.findall(r"https?://[^\s/$.?#].[^\s]*", text, re.IGNORECASE)
        cleaned = []
        for u in raw_urls:
            # Strip trailing punctuation common in sentence endings
            u_clean = u.rstrip(".,;!?:)'\"")
            if u_clean:
                cleaned.append(u_clean)
        return cleaned

    def analyze_urls(self, urls: List[str]) -> Tuple[float, List[str], bool]:
        """Analyzes URLs for shorteners, IP hosts, lookalike domains, and suspicious TLDs."""
        risk = 0.0
        reasons = []
        has_legit_domain_only = True if urls else False

        for raw_url in urls:
            try:
                # Add scheme if missing
                url = raw_url if raw_url.startswith(("http://", "https://")) else "http://" + raw_url
                parsed = urlparse(url)
                netloc = parsed.netloc.lower().split(":")[0].rstrip(".")

                # Check if matches legit domain
                is_legit = any(netloc == ld or netloc.endswith("." + ld) for ld in LEGIT_DOMAINS)
                if not is_legit:
                    has_legit_domain_only = False

                # 1. IP Link
                if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", netloc):
                    risk += 0.85
                    reasons.append(f"Direct IP link detected: {netloc}")

                # 2. URL Shortener
                if any(netloc == s or netloc.endswith("." + s) for s in SHORTENER_DOMAINS):
                    risk += 0.65
                    reasons.append(f"URL shortener masking destination: {netloc}")

                # 3. Suspicious TLD
                for tld in SUSPICIOUS_TLDS:
                    if netloc.endswith(tld):
                        risk += 0.75
                        reasons.append(f"Suspicious top-level domain ({tld}) in link: {netloc}")
                        break

                # 4. Brand Lookalike domain
                for brand in BRAND_TOKENS:
                    if brand in netloc and not is_legit:
                        # e.g. sbi-kyc.xyz or hdfc-portal.top
                        for slug in SUSPICIOUS_URL_SLUGS:
                            if slug in netloc or slug in parsed.path:
                                risk += 0.85
                                reasons.append(f"Lookalike brand domain with sensitive slug: {netloc}")
                                break
                        else:
                            risk += 0.60
                            reasons.append(f"Unverified brand keyword in external domain: {netloc}")

                # 5. Direct APK link
                if parsed.path.lower().endswith(".apk"):
                    risk += 0.90
                    reasons.append("Direct APK executable download link in message")

            except Exception:
                continue

        return min(risk, 1.0), reasons, has_legit_domain_only

    def evaluate(self, text: str, sender_id: str = "") -> Dict[str, Any]:
        """Evaluates message against Layer 1 rules with strict context exemption checks."""
        reasons = []
        risk_score = 0.0

        # --- CONTEXT RULE B: Scam Warning Exemptions ---
        # Messages that warn the user against scams must NEVER be flagged as SPAM
        if self.scam_warning_regex.search(text):
            return {
                "risk_score": 0.0,
                "reasons": ["Educational / security warning advisory against scams"],
                "is_exempt_safe": True,
                "rule_label": "SAFE"
            }

        # --- CONTEXT RULE A: Legitimate Transactional Exemptions ---
        is_bank_alert = bool(self.bank_alert_regex.search(text))
        is_otp = bool(self.otp_regex.search(text))
        is_delivery = bool(self.delivery_regex.search(text))

        urls = self.extract_urls(text)
        url_risk, url_reasons, has_legit_domain_only = self.analyze_urls(urls)

        # If it has only legitimate official domains (e.g. amazon.in, irctc.co.in) and matches transactional
        if (is_bank_alert or is_otp or is_delivery) and (not urls or has_legit_domain_only):
            exempt_reasons = []
            if is_bank_alert:
                exempt_reasons.append("Standard bank transactional account alert format")
            if is_otp:
                exempt_reasons.append("Legitimate one-time verification password (OTP)")
            if is_delivery:
                exempt_reasons.append("Transactional order delivery / travel confirmation")

            return {
                "risk_score": 0.0,
                "reasons": exempt_reasons,
                "is_exempt_safe": True,
                "rule_label": "SAFE"
            }

        # --- SCAM PATTERN DETECTION ---
        # Add URL findings
        if url_reasons:
            risk_score += url_risk
            reasons.extend(url_reasons)

        # APK download references
        if self.apk_download_regex.search(text):
            risk_score += 0.85
            reasons.append("Prompts user to install an Android APK file via SMS")

        # Specific Scam Categories
        if self.kyc_scam_regex.search(text):
            risk_score += 0.80
            reasons.append("Urgent KYC/PAN suspension or account block threat")

        if self.upi_scam_regex.search(text):
            risk_score += 0.85
            reasons.append("UPI cashback or fraudulent refund requiring PIN/link")

        if self.challan_scam_regex.search(text):
            risk_score += 0.80
            reasons.append("Fake traffic police e-challan or warrant threat")

        if self.utility_scam_regex.search(text):
            risk_score += 0.85
            reasons.append("Imminent electricity / utility disconnection scam")

        if self.courier_scam_regex.search(text):
            risk_score += 0.75
            reasons.append("Undelivered courier package address update / fee demand")

        if self.lottery_scam_regex.search(text):
            risk_score += 0.80
            reasons.append("Lottery, KBC lucky draw, or free high-value prize claim")

        if self.job_scam_regex.search(text):
            risk_score += 0.75
            reasons.append("Unrealistic daily earning part-time / Telegram job offer")

        if self.loan_scam_regex.search(text):
            risk_score += 0.75
            reasons.append("Instant pre-approved loan with zero documentation/CIBIL")

        # Obfuscation checking
        decoded_text = self.decode_obfuscation(text)
        if decoded_text != text.lower():
            if (self.kyc_scam_regex.search(decoded_text) or
                self.upi_scam_regex.search(decoded_text) or
                self.utility_scam_regex.search(decoded_text) or
                self.lottery_scam_regex.search(decoded_text) or
                self.loan_scam_regex.search(decoded_text)):
                risk_score += 0.85
                reasons.append("Obfuscated scam keywords (leetspeak / spaced characters detected)")

        # Sender ID Heuristics: personal 10-digit mobile sending official bank/legal alerts
        if sender_id:
            s_clean = re.sub(r"[^\d+]", "", sender_id)
            if (s_clean.startswith("+91") and len(s_clean) == 13) or (len(s_clean) == 10):
                if any(k in reasons for k in ["Urgent KYC/PAN suspension", "Imminent electricity"]):
                    risk_score += 0.20
                    reasons.append(f"Official bank/utility notice sent from personal mobile sender: {sender_id}")

        # Normalization
        risk_score = min(max(risk_score, 0.0), 1.0)

        # Rule label assignment
        if risk_score >= 0.70:
            rule_label = "SPAM"
        elif risk_score >= 0.35:
            rule_label = "SUSPICIOUS"
        else:
            rule_label = "SAFE"

        return {
            "risk_score": round(risk_score, 3),
            "reasons": reasons,
            "is_exempt_safe": False,
            "rule_label": rule_label
        }
