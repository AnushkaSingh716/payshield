"""Combines the text model and the link checks into one scam risk result."""
import re

from app.services import scam_text_model, url_checks

# Plain wording rules, used to explain the result in plain English
URGENCY = re.compile(
    r"\b(urgent|immediately|within 24 hours|in 24 hours|final warning|"
    r"blocked|suspended|frozen|disconnected|expired|expires)\b",
    re.IGNORECASE,
)
SENSITIVE = re.compile(
    r"\b(share|send|enter|read out|give|provide|verify|confirm|submit)\b"
    r"[^.]{0,40}\b(otp|upi pin|pin|cvv|password|aadhaar|pan)\b",
    re.IGNORECASE,
)
PRIZE = re.compile(
    r"\b(you have won|you won|winner|lottery|lucky draw|prize|congratulations|"
    r"processing fee|registration fee|clearance fee)\b",
    re.IGNORECASE,
)
COLLECT = re.compile(r"collect request", re.IGNORECASE)

# Real banks write "never share your OTP". Ignore those warning sentences.
SAFETY_PHRASE = re.compile(
    r"\b(?:do not|don't|never)\s+(?:share|asks?|give|reveal|disclose)[^.]*",
    re.IGNORECASE,
)


def label_for(score: float) -> str:
    if score < 35:
        return "Safe"
    if score < 65:
        return "Suspicious"
    return "Scam"


def wording_reasons(text: str) -> list[str]:
    """Plain-English reasons based on what the message says."""
    cleaned = SAFETY_PHRASE.sub(" ", text)
    reasons = []
    if SENSITIVE.search(cleaned):
        reasons.append("Asks for sensitive details such as OTP, PIN, CVV or Aadhaar")
    if COLLECT.search(cleaned):
        reasons.append("Asks you to accept a UPI collect request (this takes money out of your account)")
    if PRIZE.search(cleaned):
        reasons.append("Promises a prize or asks for an upfront fee")
    if URGENCY.search(cleaned):
        reasons.append("Uses urgent or threatening language to rush you")
    return reasons


def analyze_message(text: str) -> dict:
    """Score one message and explain the result."""
    text_prob = scam_text_model.text_probability(text)
    urls, link_score, link_reasons = url_checks.check_urls(text)

    # Final score: the wording counts most; risky links add on top
    risk = min(100.0, text_prob * 100 + 0.5 * link_score)
    label = label_for(risk)
    rules = wording_reasons(text)

    reasons = []  # list of (text, direction)
    if label == "Safe":
        reasons.append(("Wording looks like a normal everyday message", "decreases"))
        if not rules:
            reasons.append(
                ("No urgent threats, prize offers or requests for secret codes", "decreases")
            )
        if not urls:
            reasons.append(("No links in the message", "decreases"))
        elif not link_reasons:
            reasons.append(("Links point to normal-looking websites", "decreases"))
    else:
        reasons += [(r, "increases") for r in rules]
        reasons += [(r, "increases") for r in link_reasons]
        words = scam_text_model.top_scam_words(text) if text_prob >= 0.5 else []
        if words:
            shown = ", ".join(f'"{w}"' for w in words[:3])
            reasons.append(
                (f"Wording matches known scam messages (for example: {shown})", "increases")
            )
        if not reasons:
            reasons.append(("The wording partly resembles known scam messages", "increases"))

    return {
        "risk_score": round(risk, 1),
        "label": label,
        "text_score": round(text_prob * 100, 1),
        "link_score": round(float(link_score), 1),
        "reasons": [{"text": t, "direction": d} for t, d in reasons[:6]],
        "urls_found": urls,
    }