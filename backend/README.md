# ShieldAI Backend Classifier

The backend service is built using FastAPI and Python, implementing an online-trained machine learning model to classify phishing URLs based on domain heuristics.

## 🧠 Model Architecture & Features

### 1. Classifier Model
* **Algorithm**: Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`)
* **Estimators**: 50 Decision Trees
* **State**: Fits on a dataset of 50 samples (25 safe, 25 phishing) at startup.

### 2. Feature Extractor
For any URL submitted, a 9-dimensional numeric feature vector is extracted:
1. **URL Length**: Integer count of URL characters.
2. **HTTPS Status**: Binary flag (1 if encrypted via HTTPS, 0 if HTTP plain text).
3. **IPv4 / Digits**: Binary flag (1 if the domain resembles a raw IP address or consists of numerical digits, 0 if normal registry domain).
4. **Subdomain Depth**: Count of dots in the domain name.
5. **Sensitive Words**: Binary flag (1 if URL contains sensitive phrases like `login`, `secure`, `bank`, `verify`, `paypal`, `update`, `signin`, `support`, `account`, `webscr`, `confirm`).
6. **Domain Dash**: Binary flag (1 if domain name contains `-`).
7. **At symbol**: Binary flag (1 if `@` is in the URL).
8. **Path Redirection**: Binary flag (1 if double-slashes `//` exist in the sub-directories).
9. **URL Shorteners**: Binary flag (1 if matching known link shorteners like `bit.ly` or `tinyurl`).

---

## 🚀 Getting Started

### 1. Running the FastAPI Server
Ensure dependencies are installed:
```bash
pip install fastapi uvicorn scikit-learn numpy pydantic
```

Start the uvicorn development server:
```bash
python -m uvicorn main:app --port 8000 --reload
```

Interactive swagger API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 2. Running Unit Tests
Run the standard library test suite:
```bash
python -m unittest test_main.py
```

---

## 🔌 API Endpoints

### `POST /predict`
Analyzes a URL and returns predictions based on the decision threshold.

* **Request Body**:
```json
{
  "url": "http://paypal-secure-update.com/login",
  "include_content": true,
  "threshold": 0.5
}
```

* **Response**:
```json
{
  "url": "http://paypal-secure-update.com/login",
  "probability": 1.0,
  "is_phishing": true,
  "risk_level": "High",
  "features_extracted": {
    "url_length": 42,
    "is_https": false,
    "has_ip": false,
    "subdomain_depth": 2,
    "has_sensitive": true,
    "has_dash": true,
    "has_at": false,
    "has_redirection": false,
    "is_shortened": false
  }
}
```
