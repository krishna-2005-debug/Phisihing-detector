import os
from fastapi import FastAPI
from pydantic import BaseModel
import re
from urllib.parse import urlparse
from fastapi.middleware.cors import CORSMiddleware
from sklearn.ensemble import RandomForestClassifier
import numpy as np

app = FastAPI(title="ShieldAI Phishing Detector", version="1.2.0")

# Read allowed origins from environment (comma-separated).
# Defaults to * so local development works without any .env setup.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str
    include_content: bool = True
    threshold: float = 0.5

# Training data and Model
model = RandomForestClassifier(n_estimators=50, random_state=42)

# Simple dataset of safe and phishing URLs for online training
TRAINING_URLS = [
    # Safe URLs (Label 0)
    ("https://www.google.com", 0),
    ("https://www.wikipedia.org", 0),
    ("https://www.github.com", 0),
    ("https://www.microsoft.com", 0),
    ("https://www.apple.com", 0),
    ("https://www.amazon.com", 0),
    ("https://www.nytimes.com", 0),
    ("https://www.reddit.com", 0),
    ("https://www.netflix.com", 0),
    ("https://www.linkedin.com", 0),
    ("https://www.stackoverflow.com", 0),
    ("https://www.medium.com", 0),
    ("https://www.paypal.com", 0),
    ("https://www.chase.com", 0),
    ("https://www.bankofamerica.com", 0),
    ("https://www.facebook.com", 0),
    ("https://www.twitter.com", 0),
    ("https://www.youtube.com", 0),
    ("https://www.instagram.com", 0),
    ("https://www.spotify.com", 0),
    ("https://www.airbnb.com", 0),
    ("https://www.dropbox.com", 0),
    ("https://www.zoom.us", 0),
    ("https://www.slack.com", 0),
    ("https://www.cnn.com", 0),
    
    # Phishing URLs (Label 1)
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
]

def extract_features(url: str):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc if parsed.netloc else parsed.path.split('/')[0]
        path = parsed.path
    except Exception:
        domain = url
        path = ""
    
    url_length = len(url)
    is_https = 1 if url.startswith("https") else 0
    
    # IP address presence
    has_ip = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url) else 0
    if not has_ip:
        clean_domain = domain.replace(".", "")
        has_ip = 1 if clean_domain.isdigit() else 0

    subdomain_depth = domain.count(".")
    
    sensitive_words = ["login", "verify", "secure", "bank", "update", "signin", "paypal", "support", "account", "webscr", "confirm"]
    has_sensitive = 1 if any(word in url.lower() for word in sensitive_words) else 0
    
    has_dash = 1 if "-" in domain else 0
    has_at = 1 if "@" in url else 0
    has_redirection = 1 if "//" in path else 0
    
    shorteners = ["bit.ly", "tinyurl", "t.co", "goo.gl", "rebrand.ly", "is.gd", "ow.ly", "buff.ly"]
    is_shortened = 1 if any(short in domain.lower() for short in shorteners) else 0

    feature_dict = {
        "url_length": url_length,
        "is_https": bool(is_https),
        "has_ip": bool(has_ip),
        "subdomain_depth": subdomain_depth,
        "has_sensitive": bool(has_sensitive),
        "has_dash": bool(has_dash),
        "has_at": bool(has_at),
        "has_redirection": bool(has_redirection),
        "is_shortened": bool(is_shortened)
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
        is_shortened
    ]
    
    return feature_dict, feature_vector

# Fit the classifier at startup
@app.on_event("startup")
def train_model():
    X = []
    y = []
    for url, label in TRAINING_URLS:
        _, vector = extract_features(url)
        X.append(vector)
        y.append(label)
    
    model.fit(np.array(X), np.array(y))
    print(f"ML Model trained successfully on {len(TRAINING_URLS)} samples.")

@app.post("/predict")
def predict(req: URLRequest):
    features, vector = extract_features(req.url)
    
    # Reshape for single sample prediction
    X_sample = np.array([vector])
    
    # Predict probabilities: [prob_safe, prob_phish]
    probabilities = model.predict_proba(X_sample)[0]
    prob_phishing = round(float(probabilities[1]), 2)
    
    is_phishing = prob_phishing > req.threshold
    
    return {
        "url": req.url,
        "probability": prob_phishing,
        "is_phishing": is_phishing,
        "risk_level": "High" if prob_phishing > 0.7 else "Medium" if prob_phishing > 0.4 else "Low",
        "features_extracted": features
    }


# ── Health check ─────────────────────────────────────────────────────────────
# Render hits GET /health to confirm the service is alive after deployment.
# Returns 200 + JSON so it works with both HTTP and JSON health probes.
@app.get("/health")
def health():
    return {"status": "ok", "model_trained": model is not None}
