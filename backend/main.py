import os
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from urllib.parse import urlparse
from fastapi.middleware.cors import CORSMiddleware
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import numpy as np

@asynccontextmanager
async def lifespan(app: FastAPI):
    train_model()
    yield

app = FastAPI(title="ShieldAI Phishing Detector", version="1.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str
    include_content: bool = True
    threshold: float = 0.5

# Known safe TLDs and domains for quick-check
KNOWN_SAFE_DOMAINS = {
    "google.com", "youtube.com", "facebook.com", "wikipedia.org", "twitter.com",
    "amazon.com", "instagram.com", "reddit.com", "microsoft.com", "apple.com",
    "netflix.com", "linkedin.com", "github.com", "stackoverflow.com", "paypal.com",
    "bankofamerica.com", "chase.com", "wellsfargo.com", "cnn.com", "bbc.com",
    "nytimes.com", "medium.com", "dropbox.com", "zoom.us", "slack.com",
    "spotify.com", "airbnb.com", "shopify.com", "ebay.com", "walmart.com",
}

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "rebrand.ly",
              "is.gd", "ow.ly", "buff.ly", "short.link", "cutt.ly"}

SENSITIVE_WORDS = [
    "login", "verify", "secure", "bank", "update", "signin", "paypal",
    "support", "account", "webscr", "confirm", "password", "credential",
    "billing", "invoice", "reset", "recover", "suspend", "alert",
    "limited", "urgent", "click", "free", "prize", "winner",
]

SUSPICIOUS_TLDS = {".xyz", ".info", ".top", ".click", ".link", ".online",
                   ".site", ".club", ".tk", ".ga", ".ml", ".cf", ".gq"}

model = RandomForestClassifier(n_estimators=150, random_state=42, max_depth=8)
scaler = StandardScaler()

# ── Training dataset (100 samples, balanced) ─────────────────────────────────
TRAINING_URLS = [
    # ── Safe URLs (Label 0) ──────────────────────────────────────────────────
    ("https://www.google.com", 0),
    ("https://www.wikipedia.org/wiki/Phishing", 0),
    ("https://www.github.com/torvalds/linux", 0),
    ("https://www.microsoft.com/en-us/windows", 0),
    ("https://www.apple.com/iphone", 0),
    ("https://www.amazon.com/dp/B08N5WRWNW", 0),
    ("https://www.nytimes.com/2024/01/01/us/politics", 0),
    ("https://www.reddit.com/r/programming", 0),
    ("https://www.netflix.com/browse", 0),
    ("https://www.linkedin.com/in/profile", 0),
    ("https://stackoverflow.com/questions/tagged/python", 0),
    ("https://www.medium.com/@author/story", 0),
    ("https://www.paypal.com/us/home", 0),
    ("https://www.chase.com/personal/checking", 0),
    ("https://www.bankofamerica.com/deposits/checking", 0),
    ("https://www.facebook.com/groups/developers", 0),
    ("https://www.twitter.com/home", 0),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", 0),
    ("https://www.instagram.com/explore/tags/photography", 0),
    ("https://www.spotify.com/us/premium", 0),
    ("https://www.airbnb.com/rooms/12345", 0),
    ("https://www.dropbox.com/home", 0),
    ("https://www.zoom.us/meeting/schedule", 0),
    ("https://www.slack.com/workspace", 0),
    ("https://www.cnn.com/world", 0),
    ("https://www.bbc.com/news/technology", 0),
    ("https://www.shopify.com/store", 0),
    ("https://www.ebay.com/itm/12345678", 0),
    ("https://www.walmart.com/browse/electronics", 0),
    ("https://docs.python.org/3/library/urllib.html", 0),
    ("https://developer.mozilla.org/en-US/docs/Web", 0),
    ("https://www.cloudflare.com/learning/ddos", 0),
    ("https://www.wellsfargo.com/online-banking", 0),
    ("https://www.adobe.com/products/photoshop", 0),
    ("https://www.salesforce.com/products/crm", 0),
    ("https://www.oracle.com/database", 0),
    ("https://www.ibm.com/cloud/watson", 0),
    ("https://www.nvidia.com/en-us/graphics-cards", 0),
    ("https://www.intel.com/content/www/us/en/products", 0),
    ("https://www.samsung.com/us/smartphones", 0),
    ("https://www.sony.com/en/products/televisions", 0),
    ("https://www.cisco.com/c/en/us/solutions/networking", 0),
    ("https://www.hp.com/us-en/shop/laptops", 0),
    ("https://www.dell.com/en-us/shop/laptops", 0),
    ("https://www.lenovo.com/us/en/laptops", 0),
    ("https://news.ycombinator.com", 0),
    ("https://www.theguardian.com/technology", 0),
    ("https://techcrunch.com/category/startups", 0),
    ("https://www.wired.com/category/security", 0),
    ("https://arstechnica.com/security", 0),

    # ── Phishing URLs (Label 1) ───────────────────────────────────────────────
    ("http://secure-login-bank-verification.com/login.html", 1),
    ("http://paypal-secure-update.com/login", 1),
    ("http://signin.amazon.com-security-update.info/login", 1),
    ("http://192.168.1.105/bank/login.php", 1),
    ("http://login.microsoftonline.com-security.net", 1),
    ("http://apple-icloud-login.secure-verify.info", 1),
    ("http://verification-chase-online.com", 1),
    ("http://facebook-login-settings-recovery.xyz", 1),
    ("http://netflix-billing-update-account.com", 1),
    ("http://bit.ly/3x8FdS1", 1),
    ("http://verify-identity-paypal-resolve.com", 1),
    ("http://secure-login.chase-alert-security.com", 1),
    ("http://verification-service-online.xyz", 1),
    ("http://support-google-account.net/auth", 1),
    ("http://sign-in-ebay-verification.info", 1),
    ("http://bankofamerica-login-card-verification.com", 1),
    ("http://update-details-wellsfargo.com", 1),
    ("http://security-alert-security-update.xyz", 1),
    ("http://secure-access-banking-portal.info", 1),
    ("http://webscr-paypal-login-account.com", 1),
    ("http://recovery-microsoft-verification.org", 1),
    ("http://billing-netflix-help.net", 1),
    ("http://10.0.0.12/secure-portal/index.php", 1),
    ("http://verify-your-apple-id-now.com", 1),
    ("http://chase-bank-resolution-center.xyz", 1),
    ("http://amazon-account-suspended-verify.info/login", 1),
    ("http://secure-paypal-confirm-account.net/auth", 1),
    ("http://google-account-recovery-alert.xyz", 1),
    ("http://instagram-verify-login-support.com/account", 1),
    ("http://linkedin-verify-your-identity.info/secure", 1),
    ("http://twitter-account-suspended-appeal.xyz/login", 1),
    ("http://dropbox-file-share-access.com/signin", 1),
    ("http://zoom-meeting-invite-verify.net/join", 1),
    ("http://microsoft-365-license-expired-renew.com", 1),
    ("http://apple-support-icloud-billing-update.info", 1),
    ("http://www.secure-banking-update-required.com/login", 1),
    ("http://visa-card-verification-center.xyz", 1),
    ("http://172.16.254.1/phishing/login.html", 1),
    ("http://facebook.com.account-verify-login.info", 1),
    ("http://paypal.com.secure-login.fraudsite.net", 1),
    ("http://signin-amazon-identity-confirm.info", 1),
    ("http://netflix.com-account-billing-update.xyz", 1),
    ("http://wellsfargo-online-banking-alert.xyz/login", 1),
    ("http://chase-secure-account-alert.info/signin", 1),
    ("http://ebay-account-suspended-verify.net", 1),
    ("http://walmart-prize-winner-claim.xyz/free", 1),
    ("http://irs-tax-refund-claim-now.info/refund", 1),
    ("http://bank-credential-update-required.com/secure", 1),
    ("http://confirm-your-identity-urgent.xyz/login", 1),
    ("http://account-password-reset-alert.info/verify", 1),
]

def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate that the input looks like a real URL.
    Returns (is_valid, error_message).
    """
    if not url or len(url.strip()) < 4:
        return False, "URL is too short to be valid."

    # Must look like a URL (has a dot in the domain or is an IP)
    try:
        parsed = urlparse(url)
        # If no scheme, it's a raw hostname attempt
        if not parsed.scheme:
            return False, "Missing URL scheme. Include http:// or https://."
        if parsed.scheme not in ("http", "https"):
            return False, "Only http:// and https:// URLs are supported."

        host = parsed.hostname or ""
        if not host:
            return False, "Cannot extract a hostname from this URL."

        # Must have at least a dot in the domain (not a bare word)
        is_ip = bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host))
        is_domain = "." in host

        if not is_ip and not is_domain:
            return False, f"'{host}' does not look like a valid domain or IP address."

        # Domain labels must not be empty or contain only digits (e.g., 'bhhb' without TLD is caught above)
        if not is_ip:
            labels = host.split(".")
            tld = labels[-1]
            if len(tld) < 2:
                return False, f"The TLD '.{tld}' is not valid."

        return True, ""
    except Exception as e:
        return False, f"Could not parse URL: {e}"


def extract_features(url: str):
    try:
        parsed = urlparse(url)
        domain = parsed.hostname or (parsed.path.split('/')[0] if not parsed.netloc else parsed.netloc)
        domain = domain.lower()
        path = parsed.path
        full_url_lower = url.lower()
    except Exception:
        domain = url
        path = ""
        full_url_lower = url.lower()

    url_length = len(url)
    is_https = 1 if url.startswith("https") else 0

    # IP address presence
    has_ip = 1 if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', url) else 0

    # Subdomain depth (number of dots in hostname)
    subdomain_depth = domain.count(".")

    # Sensitive keywords in URL
    has_sensitive = 1 if any(word in full_url_lower for word in SENSITIVE_WORDS) else 0

    # Dash in domain (common phishing trick)
    has_dash = 1 if "-" in domain else 0

    # @ symbol
    has_at = 1 if "@" in url else 0

    # Double-slash in path (redirection trick)
    has_redirection = 1 if "//" in path else 0

    # Known URL shortener
    is_shortened = 1 if any(short in domain for short in SHORTENERS) else 0

    # Domain length (phishing domains tend to be longer)
    domain_length = len(domain)

    # Number of subdomains (dots minus 1)
    num_subdomains = max(0, subdomain_depth - 1)

    # Suspicious TLD
    tld = "." + domain.split(".")[-1] if "." in domain else ""
    has_suspicious_tld = 1 if tld in SUSPICIOUS_TLDS else 0

    # Digit ratio in domain
    digit_count = sum(1 for c in domain if c.isdigit())
    digit_ratio = round(digit_count / max(len(domain), 1), 2)

    # Known safe domain check
    base_domain = ".".join(domain.split(".")[-2:]) if subdomain_depth >= 1 else domain
    is_known_safe = 1 if base_domain in KNOWN_SAFE_DOMAINS else 0

    feature_dict = {
        "url_length": url_length,
        "is_https": bool(is_https),
        "has_ip": bool(has_ip),
        "subdomain_depth": subdomain_depth,
        "has_sensitive": bool(has_sensitive),
        "has_dash": bool(has_dash),
        "has_at": bool(has_at),
        "has_redirection": bool(has_redirection),
        "is_shortened": bool(is_shortened),
        "domain_length": domain_length,
        "num_subdomains": num_subdomains,
        "has_suspicious_tld": bool(has_suspicious_tld),
        "digit_ratio": digit_ratio,
        "is_known_safe": bool(is_known_safe),
    }

    feature_vector = [
        url_length,
        is_https,
        has_ip,
        subdomain_depth,
        has_sensitive,
        has_dash,
        has_at,
        has_redirection,
        is_shortened,
        domain_length,
        num_subdomains,
        has_suspicious_tld,
        digit_ratio,
        is_known_safe,
    ]

    return feature_dict, feature_vector


def train_model():
    X = []
    y = []
    for url, label in TRAINING_URLS:
        _, vector = extract_features(url)
        X.append(vector)
        y.append(label)

    X_arr = np.array(X, dtype=float)
    y_arr = np.array(y)
    scaler.fit(X_arr)
    model.fit(scaler.transform(X_arr), y_arr)
    print(f"ML Model trained on {len(TRAINING_URLS)} samples with {X_arr.shape[1]} features.")


@app.post("/predict")
def predict(req: URLRequest):
    url = req.url.strip()

    # ── Auto-prepend scheme if missing ──────────────────────────────────────
    if not re.match(r'^https?://', url, re.IGNORECASE):
        url = "http://" + url

    # ── Validate URL structure ───────────────────────────────────────────────
    valid, error_msg = validate_url(url)
    if not valid:
        raise HTTPException(status_code=422, detail=error_msg)

    features, vector = extract_features(url)

    X_sample = scaler.transform(np.array([vector], dtype=float))
    probabilities = model.predict_proba(X_sample)[0]
    prob_phishing = round(float(probabilities[1]), 3)

    # Known safe domain — hard-cap probability
    if features.get("is_known_safe"):
        prob_phishing = min(prob_phishing, 0.15)

    is_phishing = prob_phishing > req.threshold
    risk_level = "High" if prob_phishing > 0.7 else "Medium" if prob_phishing > 0.4 else "Low"

    return {
        "url": url,
        "probability": prob_phishing,
        "is_phishing": is_phishing,
        "risk_level": risk_level,
        "features_extracted": features,
    }


@app.get("/health")
def health():
    return {"status": "ok", "model_trained": True, "version": "1.3.0"}
