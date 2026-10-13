"""Rule-based checks for links inside a message."""
import re
from urllib.parse import urlparse

# Link shorteners hide where the link really goes
SHORTENERS = {
    "bit.ly", "tinyurl.com", "cutt.ly", "t.co", "goo.gl",
    "is.gd", "rb.gy", "shorturl.at", "ow.ly",
}

# Website endings that scammers use a lot (cheap to register)
BAD_TLDS = {"xyz", "top", "click", "online", "info", "buzz", "icu", "live", "site", "cfd", "link"}

# Pressure words that real bank websites rarely put in a link
KEYWORDS = [
    "kyc", "verify", "update", "secure", "login", "refund", "claim",
    "prize", "reward", "bonus", "otp", "blocked", "suspend", "unlock", "lucky",
]

# Brand name -> its real website(s). A link that mentions the brand but is on
# another website is probably a look-alike.
BRANDS = {
    "sbi": ["sbi.co.in", "onlinesbi.sbi"],
    "hdfc": ["hdfcbank.com"],
    "icici": ["icicibank.com"],
    "axis": ["axisbank.com"],
    "kotak": ["kotak.com"],
    "pnb": ["pnbindia.in"],
    "canara": ["canarabank.com"],
    "bankofbaroda": ["bankofbaroda.in"],
    "paytm": ["paytm.com"],
    "phonepe": ["phonepe.com"],
    "amazon": ["amazon.in", "amazon.com"],
    "flipkart": ["flipkart.com"],
    "swiggy": ["swiggy.com"],
    "zomato": ["zomato.com"],
    "irctc": ["irctc.co.in"],
}

# Finds links like https://..., www..., and bare short links like bit.ly/abc
_END = r"""[^\s<>"']+"""
_SHORT = "|".join(re.escape(s) for s in sorted(SHORTENERS))
URL_PATTERN = re.compile(
    rf"(?:https?://|www\.){_END}|\b(?:{_SHORT})/{_END}", re.IGNORECASE
)


def _is_official(host: str, domains: list[str]) -> bool:
    return any(host == d or host.endswith("." + d) for d in domains)


def analyze_url(url: str) -> list[tuple[int, str]]:
    """Return a list of (risk points, plain-English reason) for one link."""
    has_scheme = bool(re.match(r"https?://", url, re.IGNORECASE))
    try:
        parsed = urlparse(url if has_scheme else "//" + url)
        host = (parsed.hostname or "").lower()
    except ValueError:
        return []
    path = (parsed.path or "").lower()
    if not host:
        return []

    findings = []

    # 1. Raw IP address instead of a website name
    is_ip = bool(re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host))
    if is_ip:
        findings.append((40, f"Link uses a raw IP address ({host}) instead of a website name"))

    # 2. Shortened link
    if host in SHORTENERS:
        findings.append((25, f"Shortened link ({host}) hides the real destination"))

    # 3. No HTTPS
    if has_scheme and url.lower().startswith("http://"):
        findings.append((15, "Link is not secure (no HTTPS)"))

    # 4. Look-alike of a known brand
    tokens = re.split(r"[.\-]", host)
    for brand, official in BRANDS.items():
        mentions_brand = any(token.startswith(brand) for token in tokens)
        if mentions_brand and not _is_official(host, official):
            findings.append(
                (40, f"Look-alike website pretending to be {brand.upper()} ({host})")
            )
            break

    # 5. Pressure words in the link
    hits = [k for k in KEYWORDS if k in host + path]
    if hits:
        shown = ", ".join(f'"{k}"' for k in hits[:2])
        findings.append((15, f"Link contains pressure words like {shown}"))

    # 6. Unusual website ending
    tld = host.rsplit(".", 1)[-1]
    if not is_ip and tld in BAD_TLDS:
        findings.append((15, f"Unusual website ending (.{tld}) often used in scams"))

    # 7. Very long link
    if len(host) > 30 or len(url) > 80:
        findings.append((10, "Very long link, a common way to hide the real site"))

    findings.sort(key=lambda f: f[0], reverse=True)  # biggest risk first
    return findings


def check_urls(text: str):
    """Find every link in the text. Returns (urls, link_score 0-100, reasons)."""
    urls = []
    for match in URL_PATTERN.finditer(text):
        url = match.group(0).rstrip(".,;:!?)'\"")  # drop trailing punctuation
        if url not in urls:
            urls.append(url)

    score = 0
    reasons = []
    for url in urls:
        for points, reason in analyze_url(url):
            score += points
            if reason not in reasons:
                reasons.append(reason)

    return urls, min(100, score), reasons