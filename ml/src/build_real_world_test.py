"""Build the Real-World Evaluation Benchmark Dataset.

Strictly reserved for testing and out-of-sample evaluation.
NEVER used for training, validation, or hyperparameter selection.
Covers 18 fine-grained categories:
- bank_alert (SAFE)
- otp (SAFE)
- delivery (SAFE)
- recharge (SAFE)
- appointment (SAFE)
- casual_chat (SAFE)
- hinglish_chat (SAFE)
- promo_brand (SAFE / SUSPICIOUS)
- warning_about_scam (SAFE)
- lottery_scam (SPAM)
- kyc_scam (SPAM)
- upi_scam (SPAM)
- courier_scam (SPAM)
- job_scam (SPAM)
- loan_scam (SPAM)
- challan_scam (SPAM)
- utility_scam (SPAM)
- obfuscated_spam (SPAM)
"""
from pathlib import Path
import pandas as pd

REAL_WORLD_DATA = [
    # --- KYC SCAM (SPAM) ---
    {"text": "Dear customer, your SBI account will be blocked today. Please update your PAN immediately by visiting http://sbi-pan-kyc.xyz/update", "label": "SPAM", "category": "kyc_scam", "difficulty": "easy"},
    {"text": "HDFC Alert: Your NetBanking access is suspended due to pending KYC verification. Click http://hdfc-kyc-portal.top to avoid permanent block.", "label": "SPAM", "category": "kyc_scam", "difficulty": "easy"},
    {"text": "Dear ICICI User, your debit card has been deactivated. Complete biometric re-KYC at http://192.168.1.105/icici/login.php within 24 hours.", "label": "SPAM", "category": "kyc_scam", "difficulty": "medium"},
    {"text": "Punjab National Bank: Dear user, submit documents for KYC immediately. Download PNB_KYC_Update.apk from http://bit.ly/pnb-kyc-verify", "label": "SPAM", "category": "kyc_scam", "difficulty": "medium"},
    {"text": "Axis Bank: Your account has been temporarily frozen. Visit http://axis-online-verification.site to unlock account and restore UPI services.", "label": "SPAM", "category": "kyc_scam", "difficulty": "easy"},
    {"text": "URGENT: SBI Customer, your YONO account is locked. Update Aadhaar details today: https://sbi-yono-update.club/auth", "label": "SPAM", "category": "kyc_scam", "difficulty": "easy"},
    {"text": "Bank of Baroda: Dear Customer, Your KYC has expired. Update now to continue IMPS/NEFT transfers http://bob-support-desk.online", "label": "SPAM", "category": "kyc_scam", "difficulty": "medium"},
    {"text": "Dear Kotak Customer, your 811 account is on hold. Tap http://kotak811-kyc-renew.xyz to complete mandatory document upload.", "label": "SPAM", "category": "kyc_scam", "difficulty": "easy"},
    {"text": "Canara Bank Notice: Dear Valued Customer, please submit mandatory KYC form online at http://canarabank-portal.link or visit branch.", "label": "SPAM", "category": "kyc_scam", "difficulty": "medium"},
    {"text": "Dear A/c holder, SBI Alert: Your mobile number is delinked from savings account. Re-link at http://sbi-customer-care.icu/link", "label": "SPAM", "category": "kyc_scam", "difficulty": "medium"},
    {"text": "Paytm Payments Bank: Your wallet limit has expired. Upload PAN card copy at http://paytm-kyc-verification.top to prevent wallet closure.", "label": "SPAM", "category": "kyc_scam", "difficulty": "easy"},
    {"text": "INDUSIND ALERT: Your account credit transactions are halted. Submit KYC at http://indusind-online-check.xyz within 12 hours.", "label": "SPAM", "category": "kyc_scam", "difficulty": "medium"},

    # --- UPI SCAM (SPAM) ---
    {"text": "Congratulations! You have received a cashback reward of Rs. 1,999 in PhonePe. Claim your amount directly to bank: http://phonepe-cashback.xyz/claim", "label": "SPAM", "category": "upi_scam", "difficulty": "easy"},
    {"text": "Google Pay: You won a scratch card worth Rs 2,500! Tap here to transfer instantly to your bank account: http://gpay-rewards-claim.top", "label": "SPAM", "category": "upi_scam", "difficulty": "easy"},
    {"text": "Dear Paytm user, Rs 3000 cashback pending in your wallet. Send UPI PIN to confirm credit or click http://paytm-refund-desk.site", "label": "SPAM", "category": "upi_scam", "difficulty": "easy"},
    {"text": "PhonePe Alert: Refund of Rs 4,999 for failed transaction is ready. Click http://phonepe-refund-agent.icu and enter UPI PIN to receive money.", "label": "SPAM", "category": "upi_scam", "difficulty": "medium"},
    {"text": "BHIM UPI: Special Diwali Bonus of Rs. 5000 credited to your registered UPI ID. Accept request at http://bhim-festival-rewards.click", "label": "SPAM", "category": "upi_scam", "difficulty": "easy"},
    {"text": "GPay Reward: Your lucky draw voucher #GP882 is valid till midnight. Claim Rs 1,499 instantly: http://tinyurl.com/gpay-bonus-2026", "label": "SPAM", "category": "upi_scam", "difficulty": "medium"},
    {"text": "Cred UPI: Cash reward of INR 750 unlocked on your credit card bill. Click http://cred-reward-redeem.xyz to credit to SBI/HDFC.", "label": "SPAM", "category": "upi_scam", "difficulty": "medium"},
    {"text": "WhatsApp Pay: You received Rs 1,200 from an unknown sender. Accept or reject within 2 hours at http://wpay-receive-funds.top", "label": "SPAM", "category": "upi_scam", "difficulty": "medium"},
    {"text": "Dear customer, Rs 8,800 is credited in your UPI account. Download UPI_Receiver.apk from http://upi-payment-gateway.xyz to activate.", "label": "SPAM", "category": "upi_scam", "difficulty": "hard"},
    {"text": "Amazon Pay Cashback: Congratulations! Rs 650 credited for your recent recharge. Claim here http://amazon-pay-rewards.site/claim", "label": "SPAM", "category": "upi_scam", "difficulty": "medium"},

    # --- TRAFFIC CHALLAN SCAM (SPAM) ---
    {"text": "E-Challan Notice: Vehicle No MH02CB1234 has pending traffic fine of Rs 1,000. Pay immediately to avoid court warrant: http://echallan-parivahan-pay.xyz", "label": "SPAM", "category": "challan_scam", "difficulty": "easy"},
    {"text": "Traffic Police Department: Pending Over-speeding challan of Rs 2,000 against DL9CAA4521. Install Parivahan_Challan.apk from http://parivahan-echallan.top", "label": "SPAM", "category": "challan_scam", "difficulty": "medium"},
    {"text": "Court Summons: Lok Adalat notice issued for unpaid challan of Rs 1,500 on KA01MJ9988. Settle online today: http://delhi-traffic-challans.site", "label": "SPAM", "category": "challan_scam", "difficulty": "easy"},
    {"text": "Parivahan Sewa Alert: Final reminder to pay pending e-challans before vehicle RC suspension. Download receipt at http://echallan-mparivahan.icu", "label": "SPAM", "category": "challan_scam", "difficulty": "medium"},
    {"text": "Traffic Enforcement: Red light violation recorded on your car DL04AB3321. View CCTV proof and settle fine at http://traffic-fine-clear.xyz", "label": "SPAM", "category": "challan_scam", "difficulty": "medium"},
    {"text": "Bangalore Traffic Police: Automatic speed camera recorded 92km/h on Airport Road. Pay Rs 1000 challan immediately: http://btp-challan-pay.top", "label": "SPAM", "category": "challan_scam", "difficulty": "easy"},
    {"text": "UP Traffic Police: Challan unpaid for 90 days. Non-bailable warrant processing. Resolve now at http://up-echallan-portal.site", "label": "SPAM", "category": "challan_scam", "difficulty": "easy"},
    {"text": "Notice: Pending motor vehicle tax & challan for TS09FA7788. Download challan viewer apk: http://bit.ly/echallan-telangana-apk", "label": "SPAM", "category": "challan_scam", "difficulty": "hard"},

    # --- UTILITY / ELECTRICITY SCAM (SPAM) ---
    {"text": "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM from electric office because your previous month bill was not updated. Please immediately contact our electricity officer at 9876543210. Thank you.", "label": "SPAM", "category": "utility_scam", "difficulty": "easy"},
    {"text": "Bijli Bill Notice: Your power supply to meter #443219 will be cut off by 10 PM tonight due to unpaid dues. Call power officer Sharma at 9123456789.", "label": "SPAM", "category": "utility_scam", "difficulty": "easy"},
    {"text": "Tata Power Alert: Electricity connection scheduled for disconnection in 2 hours. Install QuickSupport app and call 9811223344 for urgent bill update.", "label": "SPAM", "category": "utility_scam", "difficulty": "medium"},
    {"text": "MSEDCL Alert: Bill payment of Rs 1,420 failed. Power cut scheduled tonight at 9:00 PM. Contact division head at 8765432190 immediately.", "label": "SPAM", "category": "utility_scam", "difficulty": "easy"},
    {"text": "BSES Yamuna Notice: Immediate power suspension notice for CA No. 100293847. To prevent disconnection, call electricity supervisor at 9312004455.", "label": "SPAM", "category": "utility_scam", "difficulty": "easy"},
    {"text": "Torrent Power: Final warning for outstanding electricity bill. Download Torrent_Pay.apk from http://torrent-power-bill.xyz to clear dues.", "label": "SPAM", "category": "utility_scam", "difficulty": "medium"},
    {"text": "DHBVN Power Alert: Your feeder connection is marked for disruption today. Call our field assistant at 9416008899 to verify your receipt.", "label": "SPAM", "category": "utility_scam", "difficulty": "medium"},
    {"text": "IGL Gas Connection: Piped natural gas connection will be blocked today due to pending safety verification. Contact manager on 9822334455.", "label": "SPAM", "category": "utility_scam", "difficulty": "easy"},

    # --- COURIER / PARCEL SCAM (SPAM) ---
    {"text": "India Post: Your parcel #IN837264589 could not be delivered due to incomplete street address. Please update your details within 12h: http://indiapost-parcel-delivery.xyz", "label": "SPAM", "category": "courier_scam", "difficulty": "easy"},
    {"text": "BlueDart Alert: Delivery failed for shipment BD883921. Re-delivery fee of Rs 5 required. Confirm address at http://bluedart-redelivery.top", "label": "SPAM", "category": "courier_scam", "difficulty": "easy"},
    {"text": "Delhivery Express: Package on hold at sorting hub. Missing flat/house number. Update delivery location immediately at http://delhivery-track-hub.site", "label": "SPAM", "category": "courier_scam", "difficulty": "medium"},
    {"text": "FedEx Notice: Your international parcel has been detained by customs. Pay clearance fee of Rs 49 to release package: http://fedex-customs-clearance.icu", "label": "SPAM", "category": "courier_scam", "difficulty": "easy"},
    {"text": "DTDC Courier: Urgent! Package awaiting dispatch. Verify recipient contact details at http://dtdc-express-logistics.xyz or package will be returned to sender.", "label": "SPAM", "category": "courier_scam", "difficulty": "medium"},
    {"text": "Speed Post Alert: Address verification required for registered article #SP99281. Click http://speedpost-service.top/verify to schedule delivery.", "label": "SPAM", "category": "courier_scam", "difficulty": "easy"},
    {"text": "DHL Express: Delivery exception occurred. Package returned to warehouse. Reschedule delivery date at http://dhl-shipment-resolver.online", "label": "SPAM", "category": "courier_scam", "difficulty": "medium"},
    {"text": "Shiprocket Delivery: Consignment #SR88473 detained due to incorrect pin code. Pay Rs 10 verification charge at http://shiprocket-track-parcel.click", "label": "SPAM", "category": "courier_scam", "difficulty": "easy"},

    # --- LOTTERY & PRIZE SCAM (SPAM) ---
    {"text": "Dear customer, congratulations! You have won Rs 25,00,000 in Kaun Banega Crorepati Jio Lucky Draw. Contact KBC manager Rana Pratap on WhatsApp +919876543211.", "label": "SPAM", "category": "lottery_scam", "difficulty": "easy"},
    {"text": "Winner Alert! Your mobile number has won a brand new Apple iPhone 16 Pro Max in Diwali Mega Contest. Claim your prize now at http://iphone-lucky-gift.xyz", "label": "SPAM", "category": "lottery_scam", "difficulty": "easy"},
    {"text": "Tata Motors Lucky Draw: Congratulations! Your phone number selected for brand new Tata Nexon SUV car. Call lottery office at 9833445566 to register.", "label": "SPAM", "category": "lottery_scam", "difficulty": "easy"},
    {"text": "YOU HAVE WON GBP 500,000 in UK International Mobile Lottery! Send your name, address, bank account to uk-lottery-claims@consultant.com to claim.", "label": "SPAM", "category": "lottery_scam", "difficulty": "easy"},
    {"text": "Big Bazaar 25th Anniversary: Claim your free Rs 10,000 shopping gift card today. Limited for first 500 users: http://bigbazaar-gift-card.top", "label": "SPAM", "category": "lottery_scam", "difficulty": "easy"},
    {"text": "Reliance Jio Reward: 50GB Free 5G data pack + Rs 500 recharge bonus credited to your SIM. Click http://jio-free-5g-bonus.site to activate.", "label": "SPAM", "category": "lottery_scam", "difficulty": "medium"},
    {"text": "Congratulations! Your ticket #88392 won Rs 1,00,000 cash in Dubai Shopping Festival. Message WhatsApp agent on 919811223344 for payout.", "label": "SPAM", "category": "lottery_scam", "difficulty": "easy"},
    {"text": "Airtel Mega Win: Your mobile number won 2nd prize of Rs 15 Lakhs in Golden Jubilee promo. Visit http://airtel-lottery-payout.icu to claim.", "label": "SPAM", "category": "lottery_scam", "difficulty": "easy"},

    # --- WORK FROM HOME & JOB SCAM (SPAM) ---
    {"text": "Work from home part-time opportunity: Earn Rs 2,500 to Rs 5,000 per day by rating hotels & liking YouTube videos. No investment needed. Contact HR Priya on Telegram @priya_hr_jobs", "label": "SPAM", "category": "job_scam", "difficulty": "easy"},
    {"text": "Amazon Online Hiring: Part-time data typing job, earn Rs 30,000 monthly. Flexible 1-2 hours daily. WhatsApp your CV to 9876501234 now.", "label": "SPAM", "category": "job_scam", "difficulty": "easy"},
    {"text": "Google India is hiring remote review evaluators. Daily payout Rs 3,500 via UPI. Limited vacancies! Join official recruitment channel: https://t.me/google_career_india", "label": "SPAM", "category": "job_scam", "difficulty": "easy"},
    {"text": "Urgent Requirement: Airport ground staff & luggage supervisor jobs available in Indigo Airlines. Salary 45,000. Apply http://indigo-airport-hiring.xyz", "label": "SPAM", "category": "job_scam", "difficulty": "medium"},
    {"text": "Earn extra income from mobile! Subscribe to merchant channels and get Rs 150 per task. Join Telegram @daily_task_earning_bot to start right now.", "label": "SPAM", "category": "job_scam", "difficulty": "easy"},
    {"text": "Flipkart Product Reviewer vacancy: Test products at home & keep them free + earn Rs 2000 daily. WhatsApp 'HI' to 918765432109 to join.", "label": "SPAM", "category": "job_scam", "difficulty": "medium"},
    {"text": "Govt Railway Recruitment 2026: 15,000 vacancies for Ticket Collector and Clerk without exam. Download admit card: http://railway-recruitment-gov.top", "label": "SPAM", "category": "job_scam", "difficulty": "medium"},
    {"text": "Work 30 mins a day on mobile! Watch movie trailers and get instant UPI payouts. Start with Rs 500 bonus: http://movie-task-rewards.site", "label": "SPAM", "category": "job_scam", "difficulty": "easy"},

    # --- INSTANT LOAN SCAM (SPAM) ---
    {"text": "Dear customer, Rs 5,00,000 instant personal loan pre-approved for your Aadhaar card at 0.5% interest. Zero document needed. Disbursal in 5 mins: http://instant-cash-loan.xyz", "label": "SPAM", "category": "loan_scam", "difficulty": "easy"},
    {"text": "Dhani Instant Loan: Rs 2,50,000 approved without CIBIL score check. Download FastLoan.apk from http://dhani-speed-loan.top and get cash in bank account.", "label": "SPAM", "category": "loan_scam", "difficulty": "medium"},
    {"text": "Bajaj Finserv: Congratulations! Your pre-approved loan of INR 7,50,000 is ready for disbursal. Click http://bajaj-quick-funds.site/apply to claim funds.", "label": "SPAM", "category": "loan_scam", "difficulty": "medium"},
    {"text": "Emergency Cash needed? Get Rs 50,000 into your account immediately. No salary slip, no guarantor. Install QuickCash from http://emergency-rupee-loan.icu", "label": "SPAM", "category": "loan_scam", "difficulty": "easy"},
    {"text": "Mudra Loan Yojana: Special subsidy of Rs 3,00,000 approved by Govt for your small business. Contact loan officer on WhatsApp 9876599881.", "label": "SPAM", "category": "loan_scam", "difficulty": "medium"},
    {"text": "KreditBee Alert: Special credit limit of Rs 1,00,000 unlocked for your PAN. Complete e-sign at http://kreditbee-instant-loan.click to disburse.", "label": "SPAM", "category": "loan_scam", "difficulty": "medium"},
    {"text": "Paytm Postpaid: Instant credit line of Rs 60,000 approved at zero processing fees. Tap http://paytm-postpaid-limit.xyz to activate.", "label": "SPAM", "category": "loan_scam", "difficulty": "medium"},
    {"text": "Low CIBIL loan solution: Get up to 10 Lakhs loan even with default history. 100% guarantee. Apply today: http://safe-rupee-credits.online", "label": "SPAM", "category": "loan_scam", "difficulty": "easy"},

    # --- OBFUSCATED SPAM (SPAM) ---
    {"text": "FR33 entry in 2 a wkly comp to win 1000 cash or iPhone 16! Txt WIN to 80085 to cl@im ur reward now. T&C apply.", "label": "SPAM", "category": "obfuscated_spam", "difficulty": "medium"},
    {"text": "Ur l0an is @pproved! Get 5,00,000 c@sh in ur b@nk t0d@y. C1ick here: http://l0an-quick.xyz or wh@ts@pp 9876543210", "label": "SPAM", "category": "obfuscated_spam", "difficulty": "hard"},
    {"text": "C.o.n.g.r.a.t.u.l.a.t.i.o.n.s! U won Rs 50,000 l@ttery. D.o.w.n.l.o.a.d apk at http://win-b0nus.top now", "label": "SPAM", "category": "obfuscated_spam", "difficulty": "hard"},
    {"text": "D3ar user ur SB! @cct will b bl0cked t0day. Upd@te k.y.c at http://sbi-k-y-c.site immediately", "label": "SPAM", "category": "obfuscated_spam", "difficulty": "hard"},
    {"text": "W0rk fr0m h0me! E@rn 3000 d@ily by lik!ng vid3os. M3ss@ge HR on t.e.l.e.g.r.a.m @job_india26", "label": "SPAM", "category": "obfuscated_spam", "difficulty": "hard"},
    {"text": "P.h.o.n.e.P.e c@shb@ck Rs 1,999 w@iting for u. Cl!ck http://tiny.cc/ph-cb to tr@nsfer to b@nk.", "label": "SPAM", "category": "obfuscated_spam", "difficulty": "hard"},
    {"text": "U.r.g.e.n.t: Y0ur p@rcel is held by p0st 0ffice. Pay 5 Rs at http://post-hub.top/rel3ase", "label": "SPAM", "category": "obfuscated_spam", "difficulty": "hard"},
    {"text": "E.l.e.c.t.r.i.c.i.t.y cut off t0night! C@ll 0fficer Sharma on 9811002233 t0 st0p disconn3ct.", "label": "SPAM", "category": "obfuscated_spam", "difficulty": "hard"},

    # --- BRAND LOOKALIKE & SUSPICIOUS PROMO (SPAM / SUSPICIOUS) ---
    {"text": "Zara Clearance Sale: Flat 90% OFF on all luxury winter jackets and perfumes for next 2 hours only! Shop now: http://zara-sale-india.xyz", "label": "SPAM", "category": "promo_brand", "difficulty": "easy"},
    {"text": "Apple India Store: Factory refurbished iPhone 15 Pro available at just Rs 14,999. Limited stock! Buy now: http://apple-india-clearance.top", "label": "SPAM", "category": "promo_brand", "difficulty": "easy"},
    {"text": "Nike Official Flash Sale: Air Jordan sneakers at 85% discount! Free shipping on prepaid orders: http://nike-outlet-clearance.site", "label": "SPAM", "category": "promo_brand", "difficulty": "easy"},
    {"text": "Tanishq Gold Jewellery: Buy 1 Get 1 Gold Coin free on Akshaya Tritiya special booking. Order at http://tanishq-gold-offers.icu", "label": "SPAM", "category": "promo_brand", "difficulty": "medium"},
    {"text": "Ray-Ban Sunglasses: Annual Warehouse Clearance! All polarized sunglasses at Rs 999. Grab deal: http://rayban-store-india.click", "label": "SPAM", "category": "promo_brand", "difficulty": "easy"},

    # --- BANK ALERT (SAFE) - Legitimate Transactional alerts ---
    {"text": "Dear SBI User, your A/c XX4892 is debited by INR 1,250.00 on 14-Oct-26 at Swiggy UPI Ref 429384729182. Avl Bal: INR 18,432.10 - SBI", "label": "SAFE", "category": "bank_alert", "difficulty": "easy"},
    {"text": "HDFC Bank: Rs 5,000.00 credited to A/c ending 1932 on 15-OCT-26 by NEFT-SALARY OCT. Net Available Balance: Rs 64,890.50.", "label": "SAFE", "category": "bank_alert", "difficulty": "easy"},
    {"text": "ICICI Bank Alert: Your Credit Card XX4019 has been charged INR 2,499.00 at AMAZON PAY INDIA on 15-Oct-26 18:22:10. Avl Limit: INR 1,45,000.00.", "label": "SAFE", "category": "bank_alert", "difficulty": "easy"},
    {"text": "Axis Bank: INR 350.00 debited from A/c no. XX9918 for Metro Travel Card recharge. If not done by you, SMS BLOCK to 5676782.", "label": "SAFE", "category": "bank_alert", "difficulty": "medium"},
    {"text": "Kotak Bank: Dear Customer, Rs. 10,000.00 transferred to Ramesh Kumar via IMPS Ref 428910294. Balance in A/c 3847 is Rs 22,400.00.", "label": "SAFE", "category": "bank_alert", "difficulty": "easy"},
    {"text": "PNB Alert: Rs 800.00 debited from Account XX7122 towards ATM Cash Withdrawal at PNB ATM Connaught Place. Avl Bal: Rs 5,230.00.", "label": "SAFE", "category": "bank_alert", "difficulty": "easy"},
    {"text": "Bank of Baroda: Your A/c ...3821 credited with INR 15,000.00 via UPI-ID brother@okaxis. Total Balance: INR 31,450.00.", "label": "SAFE", "category": "bank_alert", "difficulty": "easy"},
    {"text": "Your Union Bank A/c XX2918 has been debited for INR 45.00 towards SMS Alert Charges for Q2. Avl Bal INR 8,920.00.", "label": "SAFE", "category": "bank_alert", "difficulty": "medium"},
    {"text": "Canara Bank: INR 12,000.00 debited from A/c XX5643 via UPI Mandate for Mutual Fund SIP. Total Avl Bal: INR 44,800.00.", "label": "SAFE", "category": "bank_alert", "difficulty": "easy"},
    {"text": "IndusInd Bank: Rs 150.00 received in your Zero Balance Savings Account from UPI txn ID 428938174921.", "label": "SAFE", "category": "bank_alert", "difficulty": "easy"},
    {"text": "Federal Bank: Interest of INR 412.00 credited to your SB A/c 14820100293 for period ending Sep 2026.", "label": "SAFE", "category": "bank_alert", "difficulty": "easy"},
    {"text": "Standard Chartered: Your credit card payment of INR 18,500.00 has been received and processed with thanks.", "label": "SAFE", "category": "bank_alert", "difficulty": "easy"},

    # --- OTP MESSAGES (SAFE) ---
    {"text": "492817 is your secret One Time Password (OTP) for SBI NetBanking login. Valid for 5 minutes. Do NOT share OTP with anyone.", "label": "SAFE", "category": "otp", "difficulty": "easy"},
    {"text": "Your OTP for Aadhaar authentication is 839201. UIDAI never calls to ask for OTP. Valid for 10 minutes.", "label": "SAFE", "category": "otp", "difficulty": "easy"},
    {"text": "736192 is the verification code to log into your Zomato account. Please do not share this code with delivery partner or anyone else.", "label": "SAFE", "category": "otp", "difficulty": "easy"},
    {"text": "Use code 193820 for Swiggy account verification. Never share this OTP with anyone, including Swiggy customer care agents.", "label": "SAFE", "category": "otp", "difficulty": "easy"},
    {"text": "829104 is your verification code for Amazon order #402-8374628. Code expires in 15 minutes.", "label": "SAFE", "category": "otp", "difficulty": "easy"},
    {"text": "Your Google verification code is 552918. Never share your verification code with anyone.", "label": "SAFE", "category": "otp", "difficulty": "easy"},
    {"text": "WhatsApp code: 482-194. You can also tap on the link to verify your phone: v.whatsapp.com/482194. Do not share this code.", "label": "SAFE", "category": "otp", "difficulty": "medium"},
    {"text": "918234 is your OTP for HDFC Bank card payment of INR 850.00 at BookMyShow. Bank never asks for OTP or CVV.", "label": "SAFE", "category": "otp", "difficulty": "easy"},
    {"text": "CoWIN: Your OTP for vaccine certificate download is 662910. Valid for 3 mins.", "label": "SAFE", "category": "otp", "difficulty": "easy"},
    {"text": "Flipkart verification code: 394812. Use this code to sign in to your Flipkart account. Happy Shopping!", "label": "SAFE", "category": "otp", "difficulty": "easy"},
    {"text": "Uber code: 7192. Never share this code with your driver. Share only the 4-digit PIN when trip starts.", "label": "SAFE", "category": "otp", "difficulty": "easy"},
    {"text": "Ola OTP: Your ride PIN is 4421. Share with driver after boarding the cab.", "label": "SAFE", "category": "otp", "difficulty": "easy"},

    # --- DELIVERY UPDATES (SAFE) ---
    {"text": "Your Amazon package with order #402-1928374 is out for delivery today with delivery associate Ramesh Kumar. Share delivery code 48 upon receipt.", "label": "SAFE", "category": "delivery", "difficulty": "easy"},
    {"text": "Flipkart Update: Shipment FMPC48291024 is out for delivery. Wishmaster Sunil will deliver your product by 7:00 PM today.", "label": "SAFE", "category": "delivery", "difficulty": "easy"},
    {"text": "Blinkit: Your grocery order #BK99283 is out for delivery and will arrive in 9 minutes. Track live on Blinkit app.", "label": "SAFE", "category": "delivery", "difficulty": "easy"},
    {"text": "Zepto: Hurray! Your order containing Fresh Milk and Fruits has been delivered. Thank you for shopping with Zepto.", "label": "SAFE", "category": "delivery", "difficulty": "easy"},
    {"text": "BlueDart: Your consignment 482910384 from HDFC Bank Cards division has been delivered on 15-OCT-26 to Bangalore. Signed by self.", "label": "SAFE", "category": "delivery", "difficulty": "medium"},
    {"text": "Delhivery: Waybill #98472910243 is arriving today between 2 PM and 5 PM. Track live at https://www.delhivery.com/track/package/98472910243", "label": "SAFE", "category": "delivery", "difficulty": "medium"},
    {"text": "Myntra: Order #19827394 has been shipped via Shadowfax. Expected delivery by Thursday, 17th Oct.", "label": "SAFE", "category": "delivery", "difficulty": "easy"},
    {"text": "Dunzo Daily: Delivery partner is at your doorstep with order #DZ48291. Please collect your items.", "label": "SAFE", "category": "delivery", "difficulty": "easy"},

    # --- RECHARGE & BILL CONFIRMATION (SAFE) ---
    {"text": "Recharge of Rs 299 is successful for your Jio number 9820012345. Benefits: 1.5GB/day, Unlimited Calls, 100 SMS/day. Validity: 28 days. Thank you.", "label": "SAFE", "category": "recharge", "difficulty": "easy"},
    {"text": "Airtel: Recharge of Rs 719 successful for 9845012345. Unlimited calls + 1.5GB/day for 84 days activated. Enjoy Airtel 5G Plus.", "label": "SAFE", "category": "recharge", "difficulty": "easy"},
    {"text": "Vi (Vodafone Idea): Payment of Rs 459 received for Postpaid Bill of mobile 9890012345. Your outstanding balance is now Rs 0.00.", "label": "SAFE", "category": "recharge", "difficulty": "easy"},
    {"text": "Tata Play: Recharge of Rs 450 received for Subscriber ID 1092837465. Your account balance is Rs 512.50. Next recharge due on 18-Nov-26.", "label": "SAFE", "category": "recharge", "difficulty": "easy"},
    {"text": "ACT Fibernet: Payment of Rs 1,179 successful for Account #10492837. Your high-speed broadband plan is active till 15-Nov-2026.", "label": "SAFE", "category": "recharge", "difficulty": "easy"},
    {"text": "FASTag Alert: FASTag recharge of INR 1,000 for vehicle KA04MH1234 successful. Updated FASTag wallet balance: INR 1,420.00.", "label": "SAFE", "category": "recharge", "difficulty": "easy"},
    {"text": "JioFiber: Plan renewal successful! 100 Mbps Unlimited Data plan is renewed for 30 days on your connection 08029384729.", "label": "SAFE", "category": "recharge", "difficulty": "easy"},

    # --- APPOINTMENT & SERVICE REMINDER (SAFE) ---
    {"text": "Reminder: Your dental check-up with Dr. Sneha Rao at Apollo Dental Clinic is confirmed for tomorrow, 16-Oct-26 at 4:30 PM. Please arrive 10 mins early.", "label": "SAFE", "category": "appointment", "difficulty": "easy"},
    {"text": "Practo: Appointment booked with Dr. Mehta (Cardiologist) for Saturday 18-Oct at 11:00 AM at Max Super Speciality Hospital, Saket.", "label": "SAFE", "category": "appointment", "difficulty": "easy"},
    {"text": "Urban Company: Professional Rajesh will visit your home tomorrow at 10:00 AM for AC Deep Cleaning service. Booking ID: #UC928374.", "label": "SAFE", "category": "appointment", "difficulty": "easy"},
    {"text": "Maruti Service: Your Baleno KA03NA4422 is due for 3rd free service. Contact Bimal Auto Bangalore at 080-2839401 to book service slot.", "label": "SAFE", "category": "appointment", "difficulty": "easy"},
    {"text": "Dr Lal PathLabs: Phlebotomist Ramesh will visit tomorrow at 7:30 AM for home sample collection. Fasting of 10-12 hours required.", "label": "SAFE", "category": "appointment", "difficulty": "easy"},
    {"text": "Cult.fit: Your slot for HRX Workout at Indiranagar Center is booked for today at 6:30 PM. Please carry your workout towel and shoes.", "label": "SAFE", "category": "appointment", "difficulty": "easy"},
    {"text": "Passport Seva: Appointment confirmed at PSK Bangalore East for Tatkaal application on 20-Oct-2026 at 09:45 AM. Carry original documents.", "label": "SAFE", "category": "appointment", "difficulty": "medium"},

    # --- CASUAL CHAT & HINGLISH CHAT (SAFE) ---
    {"text": "Bhai shaam ko kahan milna hai? 6 baje CCD chalte hain ya seedha office ke baad ghar aayega?", "label": "SAFE", "category": "hinglish_chat", "difficulty": "easy"},
    {"text": "Kal subah 9 baje college chalna hai kya? Assignment submit karne ki last date hai kal.", "label": "SAFE", "category": "hinglish_chat", "difficulty": "easy"},
    {"text": "Mummy boli market se aate waqt dahi aur dhaniya lete aana. Mat bhoolna please.", "label": "SAFE", "category": "hinglish_chat", "difficulty": "easy"},
    {"text": "Bhai tera laptop ka charger mere bag mein reh gaya tha. Kal subah office aate hue le aunga.", "label": "SAFE", "category": "hinglish_chat", "difficulty": "easy"},
    {"text": "Hey, did you review the pull request I created on GitHub? Let me know if you need any changes.", "label": "SAFE", "category": "casual_chat", "difficulty": "easy"},
    {"text": "Can you share the Uber location with me? Traffic is crazy near Silk Board junction right now.", "label": "SAFE", "category": "casual_chat", "difficulty": "easy"},
    {"text": "Happy Birthday dear! May this year bring you abundant happiness, great health and immense success.", "label": "SAFE", "category": "casual_chat", "difficulty": "easy"},
    {"text": "Are you joining the standup call in 5 mins? The team is waiting for the sprint demo.", "label": "SAFE", "category": "casual_chat", "difficulty": "easy"},
    {"text": "Haan bhai main theek hoon. Weekend par cricket match khelte hain ground par. Batting teri pehle hogi.", "label": "SAFE", "category": "hinglish_chat", "difficulty": "easy"},
    {"text": "Lunch kar liya kya? Aaj canteen mein paneer butter masala bana hai, jaldi aao.", "label": "SAFE", "category": "hinglish_chat", "difficulty": "easy"},
    {"text": "Bro send me notes of machine learning chapter 3, exams are starting next Monday.", "label": "SAFE", "category": "casual_chat", "difficulty": "easy"},
    {"text": "Railway ticket confirm ho gaya hai 3AC mein. Main shaam ko packing start karunga.", "label": "SAFE", "category": "hinglish_chat", "difficulty": "easy"},

    # --- SCAM WARNINGS & EDUCATIONAL MESSAGES (SAFE) ---
    # CONTEXT RULE: Messages warning users about scams should NEVER be flagged as SPAM
    {"text": "Security Warning from SBI: Never share your OTP, UPI PIN, Password or CVV with anyone. Bank never calls or sends SMS asking for confidential credentials.", "label": "SAFE", "category": "warning_about_scam", "difficulty": "medium"},
    {"text": "Alert: Beware of fake SMS claiming electricity bill unpaid or power cut tonight. It is a scam, do not call unknown phone numbers or click any links.", "label": "SAFE", "category": "warning_about_scam", "difficulty": "hard"},
    {"text": "Cyber Dost Advisory: Beware of part-time job scams offering money for liking YouTube videos or review rating on Telegram. Never transfer money to unknown accounts.", "label": "SAFE", "category": "warning_about_scam", "difficulty": "hard"},
    {"text": "HDFC Security Tip: It's a scam, don't click on any link promising lottery prizes or instant loans without documentation. Always verify through official app.", "label": "SAFE", "category": "warning_about_scam", "difficulty": "hard"},
    {"text": "RBI Kehta Hai: Do not click on unknown links claiming KYC update or account block. Report unauthorized transactions to 1930 immediately.", "label": "SAFE", "category": "warning_about_scam", "difficulty": "hard"},
    {"text": "TRAI Alert: TRAI never disconnects mobile numbers or sends disconnection notices. Ignore fraudulent calls threatening disconnection of mobile services.", "label": "SAFE", "category": "warning_about_scam", "difficulty": "hard"},
    {"text": "Delhi Police Advisory: Fake e-challan SMS circulating with malicious APK files. Only check and pay official challans on https://echallan.parivahan.gov.in.", "label": "SAFE", "category": "warning_about_scam", "difficulty": "hard"},
    {"text": "Warning: Do not accept unknown collect requests or enter your UPI PIN to receive money. Entering UPI PIN will DEBIT money from your account.", "label": "SAFE", "category": "warning_about_scam", "difficulty": "hard"},

    # --- LEGITIMATE BRAND PROMOTIONS (SAFE / PROMOTIONS) ---
    # CONTEXT RULE: Legitimate official brand promotions with official domain names or shortcodes
    {"text": "Domino's Pizza: Craving hot pizza? Enjoy Flat 40% OFF up to Rs 100 on orders above Rs 249. Use coupon DOM40 on official Domino's App or https://dominos.co.in", "label": "SAFE", "category": "promo_brand", "difficulty": "medium"},
    {"text": "Amazon Great Indian Festival: Early access is now live for Prime members. Huge discounts on electronics and fashion. Explore on https://amazon.in", "label": "SAFE", "category": "promo_brand", "difficulty": "medium"},
    {"text": "Flipkart Big Billion Days: Sale begins midnight tonight! Extra 10% instant discount on Axis Bank and ICICI Bank credit cards on https://flipkart.com", "label": "SAFE", "category": "promo_brand", "difficulty": "medium"},
    {"text": "Swiggy Gourmet: Get flat Rs 125 off on fine dining restaurants this weekend with code GOURMET125. Order delicious meals on Swiggy App.", "label": "SAFE", "category": "promo_brand", "difficulty": "medium"},
    {"text": "BookMyShow: Blockbuster weekend! Book tickets for IMAX movies and get 50% discount on 2nd ticket using Kotak Card. Valid on https://bookmyshow.com", "label": "SAFE", "category": "promo_brand", "difficulty": "medium"},
    {"text": "Zomato Gold: Renew your Gold membership today at just Rs 99 for 3 months and enjoy unlimited free deliveries and VIP dining discounts.", "label": "SAFE", "category": "promo_brand", "difficulty": "medium"}
]

# Duplicate expansion to reach exactly ~200 items with variations
def build_expanded_test_set():
    import copy
    all_items = copy.deepcopy(REAL_WORLD_DATA)
    
    # Add variations for bank alerts
    banks = ["Canara Bank", "Union Bank", "Bank of India", "IDFC First Bank", "Yes Bank"]
    for i, b in enumerate(banks):
        all_items.append({
            "text": f"Dear {b} Customer, your A/c XX{3100+i*11} is debited by INR {450+i*100}.00 on 15-Oct-26 at Merchant Store UPI Ref {948291024+i}. Avl Bal: INR {15200+i*500}.00.",
            "label": "SAFE",
            "category": "bank_alert",
            "difficulty": "easy"
        })
    
    # Add variations for OTPs
    services = ["Swiggy", "Zomato", "Myntra", "Ajio", "Flipkart", "MakeMyTrip", "IRCTC", "Zepto", "Blinkit", "BigBasket"]
    for i, s in enumerate(services):
        all_items.append({
            "text": f"{291040 + i*7} is your secret One Time Password (OTP) for {s} login verification. Valid for 5 minutes. Never share OTP with anyone.",
            "label": "SAFE",
            "category": "otp",
            "difficulty": "easy"
        })

    # Add variations for casual Hinglish chat
    hinglish_phrases = [
        "Bhai kal subah badminton khelne aayega kya? Court book kar diya hai maine 7 baje.",
        "Arey yaar aaj auto nahi mil raha tha, isliye 15 minute late ho gaya office mein.",
        "Kal ka movie plan confirm hai na? Main tickets book kar doon PVR Forum mall mein?",
        "Bhai salary aa gayi kya teri? Meri company ne aaj subah credit kar di.",
        "Mera laptop restart ho raha hai bar bar, shaam ko aake thoda dekh lega please?",
        "Ghar pe sab theek hain na? Aunty ji ka health kaisa hai abhi?",
        "Bhai assignment ka link share kar de please, upload karne ka time khatam hone wala hai.",
        "Chai peene chalte hain neeche, 10 minute ka break lete hain work se.",
        "Kal weekend pe highway par long drive chalte hain doston ke saath.",
        "Maine tera jacket return kar diya tha table par, check kar lena."
    ]
    for h in hinglish_phrases:
        all_items.append({
            "text": h,
            "label": "SAFE",
            "category": "hinglish_chat",
            "difficulty": "easy"
        })

    # Add variations for Delivery
    couriers = ["FedEx Express", "BlueDart Logistics", "Delhivery Logistics", "Ekart Logistics", "Shadowfax"]
    for i, c in enumerate(couriers):
        all_items.append({
            "text": f"Your order #{50291024 + i*17} has been shipped via {c}. Track your shipment on the official app. Expected delivery within 2 days.",
            "label": "SAFE",
            "category": "delivery",
            "difficulty": "easy"
        })

    # Add variations for KYC Scam
    kyc_variants = [
        "PNB Alert: Your debit card is blocked due to non-submission of KYC form. Tap http://pnb-kyc-desk.site to activate instantly.",
        "Central Bank of India: Complete your PAN-Aadhaar linking at http://cbi-online-pan.top to continue receiving direct benefit transfers.",
        "Kotak 811 Notice: Your mobile banking is disabled. Upload self-attested Aadhaar at http://kotak-mobile-kyc.xyz/login today.",
        "IDBI Bank: Dear customer, your netbanking facility will terminate today. Re-verify KYC now: http://idbi-secure-portal.icu",
        "RBL Bank Alert: Account suspended due to expired KYC documentation. Follow http://rbl-kyc-verify.click to reactivate immediately.",
        "UCO Bank Alert: Immediate update required for dormant account. Click http://uco-banking-online.top to avoid permanent closure."
    ]
    for k in kyc_variants:
        all_items.append({
            "text": k,
            "label": "SPAM",
            "category": "kyc_scam",
            "difficulty": "medium"
        })

    # Add variations for UPI Scam
    upi_variants = [
        "PhonePe Gift Card: You won Rs 3,499 in monthly cashback bumper draw! Transfer to bank: http://phonepe-gift-reward.xyz",
        "Paytm Merchant Offer: Congratulations, Rs 1,500 festive refund is credited to your wallet. Accept via http://paytm-refund-desk.top",
        "Google Pay Scratch Card: Win up to Rs 4,000 today. Scratch now on http://gpay-scratch-bonanza.site before offer expires at 11:59 PM.",
        "BHIM UPI Bonus: Special Govt subsidy of Rs 2,500 credited to your registered UPI ID. Claim at http://bhim-subsidy-claim.icu",
        "Cred Cash: Rs 1,200 instant cashback ready for withdrawal. Tap http://cred-bonus-payout.click and enter UPI ID."
    ]
    for u in upi_variants:
        all_items.append({
            "text": u,
            "label": "SPAM",
            "category": "upi_scam",
            "difficulty": "medium"
        })

    # Add variations for Challan Scam
    challan_variants = [
        "Haryana Police: E-challan pending against HR26DK3920. Settle fine of Rs 500 at http://echallan-haryana-gov.site to avoid court proceedings.",
        "Rajasthan Transport: Over-speed violation fine Rs 1,000 registered on RJ14CA9012. Pay now: http://rajasthan-challan-portal.top",
        "Kolkata Traffic Police: Dangerous driving notice issued against WB02AK1122. Pay online: http://kolkata-traffic-fine.xyz",
        "Gujarat Parivahan: Notice of vehicle impoundment for pending traffic violations on GJ01BC4455. Settle fine at http://gujarat-echallan.icu"
    ]
    for ch in challan_variants:
        all_items.append({
            "text": ch,
            "label": "SPAM",
            "category": "challan_scam",
            "difficulty": "medium"
        })

    # Add variations for Utility Scam
    utility_variants = [
        "Dear Electricity Consumer, your light will be disconnected tonight at 10:00 PM due to unpaid balance of Rs 1,890. Call electricity officer at 9876512340.",
        "PSPCL Power Alert: Meter connection #554433 scheduled for disconnection tonight. Call helpline officer immediately on 9123456780.",
        "JVVNL Notice: Final intimation for non-payment of electricity bill. Power will be cut in 1 hour. Contact billing executive at 9811223399.",
        "TNEB Tamil Nadu: Power supply to consumer #889922 will be disconnected tonight at 9:30 PM. Call engineer at 9840123456 to resolve."
    ]
    for ut in utility_variants:
        all_items.append({
            "text": ut,
            "label": "SPAM",
            "category": "utility_scam",
            "difficulty": "easy"
        })

    # Add variations for Courier Scam
    courier_variants = [
        "India Post: Shipment #IP982736281 detained at regional post office due to invalid zip code. Pay Rs 25 re-routing fee at http://indiapost-parcel-reschedule.xyz",
        "BlueDart Courier: Package delivery failed as consignee was unreachable. Update delivery date & phone at http://bluedart-package-tracker.top",
        "DTDC Express: Your parcel has arrived at local facility with unpaid postage of Rs 35. Release parcel at http://dtdc-package-release.site",
        "FedEx Express: Action required: Your incoming consignment is pending customs declaration. Complete form at http://fedex-customs-portal.icu"
    ]
    for cr in courier_variants:
        all_items.append({
            "text": cr,
            "label": "SPAM",
            "category": "courier_scam",
            "difficulty": "medium"
        })

    # Add variations for Job Scam
    job_variants = [
        "Amazon India Part Time: Earn Rs 4,000 per day working from home. Simple mobile task like product review. Contact manager on WhatsApp 9876541239.",
        "YouTube Partner Program: Earn Rs 250 for every video like & subscribe. Daily payment directly to UPI. Join Telegram @youtube_daily_tasks_india.",
        "Netflix Movie Reviewer: Watch latest movie trailers and get paid Rs 1,500 daily. WhatsApp 'APPLY' to 919811002244 to start right away.",
        "Data Entry Remote Job: Earn Rs 25,000 per month typing PDF to Word from home. Zero registration fees. Register at http://online-typing-careers.xyz"
    ]
    for j in job_variants:
        all_items.append({
            "text": j,
            "label": "SPAM",
            "category": "job_scam",
            "difficulty": "easy"
        })

    # Add variations for Loan Scam
    loan_variants = [
        "Pre-approved loan offer! Rs 10 Lakhs loan sanctioned on your Aadhaar card with 1% monthly interest. No paperwork. Apply at http://rupee-instant-loan.xyz",
        "Zero CIBIL loan: Get Rs 1,50,000 cash in your bank in 15 minutes. Install PaisaFast.apk from http://fast-paisa-loan.top now.",
        "KreditBee Pre-Approval: Pre-approved personal loan of Rs 3,00,000 ready for disbursal. Tap http://kreditbee-quick-disbursal.site to accept.",
        "Govt Subsidy Loan: PM Mudra Loan of Rs 5 Lakhs sanctioned at 0% processing fees. Contact loan agent on WhatsApp 9822334411."
    ]
    for l in loan_variants:
        all_items.append({
            "text": l,
            "label": "SPAM",
            "category": "loan_scam",
            "difficulty": "medium"
        })

    # Add variations for Obfuscated Spam
    obf_variants = [
        "G.e.t  f.r.e.e  Rs 50,000 l.o.a.n  in 5 m.i.n.s! C.l.i.c.k  h.e.r.e: http://f-r-e-e-l-o-a-n.xyz",
        "SB! A/c al3rt: Ur @cct is bl0cked t0day! Upd@te k.y.c at http://sbi-k-y-c.icu immediately",
        "W!n iPhone 16 Pr0 M@x in D!wal! Lucky Dr@w! Cl@im n0w at http://i-p-h-o-n-e.top",
        "Y0ur p0wer will b3 cut off t0n!ght at 9:30 PM. C@ll electric officer on 9876509876",
        "Wh@ts@pp us on 9811223344 to e@rn 4000 d@ily by w0rking fr0m h0me."
    ]
    for o in obf_variants:
        all_items.append({
            "text": o,
            "label": "SPAM",
            "category": "obfuscated_spam",
            "difficulty": "hard"
        })

    df = pd.DataFrame(all_items).drop_duplicates(subset=["text"])
    return df


if __name__ == "__main__":
    out_path = Path(__file__).resolve().parent.parent / "data" / "real_world_test.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = build_expanded_test_set()
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} real-world evaluation test messages saved to {out_path}")
    print("\nCounts by label:")
    print(df["label"].value_counts())
    print("\nCounts by category:")
    print(df["category"].value_counts())
    print("\nCounts by difficulty:")
    print(df["difficulty"].value_counts())
