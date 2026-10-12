"""Creates a small labeled dataset of scam (1) and safe (0) messages.

This is demo data built from templates. Real scams vary more, so we keep
the model simple and combine it with rule-based link checks later.
"""
import random
import string
from pathlib import Path

import pandas as pd

random.seed(42)
N_PER_CLASS = 800

BANKS = ["SBI", "HDFC", "ICICI", "Axis", "PNB", "Kotak", "Bank of Baroda", "Canara"]
NAMES = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anita", "Rohan", "Neha",
         "Suresh", "Pooja"]
APPS = ["Paytm", "PhonePe", "Google Pay", "Amazon", "Flipkart", "Swiggy", "Zomato"]
TLDS = ["xyz", "top", "info", "click", "online"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
          "Nov", "Dec"]
PRIZES = ["10,00,000", "25,00,000", "5,00,000", "50,000", "1 crore"]


def rand_digits(n):
    return "".join(random.choices(string.digits, k=n))


def rand_code(n):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def bad_link(bank):
    """Scam-style links: look-alike domain, shortened, IP-based, or no HTTPS."""
    b = bank.lower().replace(" ", "")
    kind = random.choice(["lookalike", "short", "ip", "http"])
    if kind == "lookalike":
        word = random.choice(["update", "verify", "secure"])
        return f"https://{b}-kyc-{word}.{random.choice(TLDS)}/{rand_code(5)}"
    if kind == "short":
        return f"{random.choice(['bit.ly', 'tinyurl.com', 'cutt.ly'])}/{rand_code(6)}"
    if kind == "ip":
        return f"http://203.0.113.{random.randint(1, 254)}/{rand_code(5)}"
    return f"http://{b}-care.{random.choice(TLDS)}/login"


def good_link(bank):
    """Normal links from well-known sites."""
    return random.choice([
        "https://www.amazon.in/orders", "https://www.hdfcbank.com",
        "https://www.sbi.co.in", "https://www.irctc.co.in",
        "https://www.flipkart.com/orders", "https://www.swiggy.com",
    ])


# (category, template) pairs. {slots} are filled with random values.
SCAM_TEMPLATES = [
    ("fake_kyc", "Dear customer, your {bank} account will be blocked today. Update your KYC immediately: {link}"),
    ("fake_kyc", "URGENT: {bank} KYC expired. Your account will be suspended in 24 hours. Click {link} to verify PAN now. Ref {ref}"),
    ("fake_kyc", "{bank} Alert: Your KYC is pending. Share Aadhaar and PAN at {link} or your account will be frozen. Ref {ref}"),
    ("lottery", "Congratulations {name}! You have won Rs {prize} in the KBC lucky draw. To claim your prize pay a processing fee of Rs {fee}. Call {phone}"),
    ("lottery", "You won a lottery of Rs {prize}! Send your bank details to claim. WhatsApp {phone}. Ref {ref}"),
    ("lottery", "Lucky winner {name}! {app} has selected you for a free iPhone worth Rs {amount}. Claim now: {link}"),
    ("upi_refund", "Your {app} refund of Rs {amount} is pending. Enter your UPI PIN at {link} to receive the money. Ref {ref}"),
    ("upi_refund", "Please accept the collect request of Rs {amount} to receive your refund. {app} ref {ref}"),
    ("upi_refund", "Refund of Rs {amount} initiated. Share your UPI PIN to confirm. Call {phone}. Ref {ref}"),
    ("otp", "Sir, a code was sent to your phone by mistake. Kindly read out the OTP to verify your {bank} account. Ref {ref}"),
    ("otp", "{bank} security team: share your OTP and CVV to stop the debit of Rs {amount}. Call {phone} immediately"),
    ("electricity", "Dear consumer, your electricity will be disconnected tonight at 9:30 PM due to unpaid bill of Rs {amount}. Call {phone} immediately. Ref {ref}"),
    ("job", "Work from home! Earn Rs {amount} daily by liking videos. Join now on WhatsApp {phone}. Registration fee Rs {fee}"),
    ("parcel", "Your parcel is held at customs. Pay Rs {fee} clearance fee at {link} to release it. Ref {ref}"),
    ("tax_loan", "Income Tax refund of Rs {amount} approved. Verify your bank details at {link} to receive it. Ref {ref}"),
    ("tax_loan", "Instant loan of Rs {amount} approved without documents! Pay Rs {fee} processing fee at {link}. Ref {ref}"),
]

SAFE_TEMPLATES = [
    ("bank_debit", "Rs {amount} debited from your {bank} account ending {last4} on {date}. If this was not you, call the number on the back of your card."),
    ("bank_credit", "Your {bank} account has been credited with Rs {amount} on {date}. Ref {ref}"),
    ("otp_real", "{otp} is your OTP for {app}. Do not share it with anyone. Valid for 10 minutes."),
    ("delivery", "Hi {name}, your {app} order {ref} has been shipped and will arrive by {date}. Track at {link}"),
    ("chat", "Hey {name}, are we still meeting for dinner at {time}? Let me know."),
    ("bill_reminder", "Reminder: your electricity bill of Rs {amount} is due on {date}. Pay using the official app. Ref {ref}"),
    ("appointment", "Your appointment with Dr. {name} is confirmed for {date} at {time}. Reply C to cancel."),
    ("real_refund", "Thank you for shopping with {app}. Your refund of Rs {amount} has been credited to your original payment method. Ref {ref}"),
    ("awareness", "{bank} never asks for your OTP, PIN or CVV. Beware of fraud calls. Visit {link} for safety tips. Ref {ref}"),
    ("kyc_done", "Hi {name}, your KYC has been verified successfully. Thank you for banking with {bank}. Ref {ref}"),
    ("travel", "Your train ticket PNR {ref} is confirmed for {date}. Check status at {link}"),
    ("payment_ok", "Your Rs {amount} {app} bill payment was successful. Txn ID {ref}."),
]


def fill(template, link_fn):
    """Replace the {slots} in a template with random values."""
    bank = random.choice(BANKS)
    text = template.format(
        bank=bank,
        name=random.choice(NAMES),
        app=random.choice(APPS),
        amount=random.randint(100, 99999),
        prize=random.choice(PRIZES),
        fee=random.choice([499, 999, 1500, 2500, 4999]),
        phone="98XXXXXX" + rand_digits(2),  # masked fake number
        ref=rand_digits(6),
        otp=rand_digits(6),
        last4=rand_digits(4),
        date=f"{random.randint(1, 28):02d}-{random.choice(MONTHS)}",
        time=f"{random.randint(1, 12)}:{random.choice(['00', '15', '30', '45'])} "
             f"{random.choice(['AM', 'PM'])}",
        link=link_fn(bank),
    )
    if random.random() < 0.15:  # some messages in CAPS, for both classes
        text = text.upper()
    return text


def build(templates, link_fn, label, n):
    """Make n unique messages from the templates."""
    rows, seen, attempts = [], set(), 0
    while len(rows) < n and attempts < n * 50:
        attempts += 1
        category, template = random.choice(templates)
        text = fill(template, link_fn)
        if text in seen:
            continue
        seen.add(text)
        rows.append({"text": text, "label": label, "category": category})
    return rows


rows = build(SCAM_TEMPLATES, bad_link, 1, N_PER_CLASS)
rows += build(SAFE_TEMPLATES, good_link, 0, N_PER_CLASS)

df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)

out_path = Path(__file__).parent / "data" / "scam_messages.csv"
df.to_csv(out_path, index=False)

print(f"Saved {len(df):,} messages to {out_path}")
print()
print("Label counts (0 = safe, 1 = scam):")
print(df["label"].value_counts().to_string())
print()
print("Examples:")
for label in (1, 0):
    for text in df[df["label"] == label]["text"].head(2):
        print(f"  [{'SCAM' if label else 'SAFE'}] {text}")
        