import unittest
from fastapi.testclient import TestClient
from main import app, extract_features, validate_url, train_model

# Use the client as a context manager so the lifespan (train_model) fires.
client = TestClient(app, raise_server_exceptions=True)


class TestURLValidation(unittest.TestCase):

    def test_valid_https_url(self):
        valid, msg = validate_url("https://www.google.com")
        self.assertTrue(valid, msg)

    def test_valid_http_url_with_path(self):
        valid, msg = validate_url("http://example.com/path/to/page?q=1")
        self.assertTrue(valid, msg)

    def test_valid_ip_url(self):
        valid, msg = validate_url("http://192.168.1.1/login.php")
        self.assertTrue(valid, msg)

    def test_invalid_bare_word(self):
        # 'bhhb' — no TLD, no dot — should be rejected
        valid, msg = validate_url("http://bhhb")
        self.assertFalse(valid)
        self.assertTrue(len(msg) > 0)

    def test_invalid_empty(self):
        valid, msg = validate_url("")
        self.assertFalse(valid)

    def test_invalid_too_short(self):
        valid, msg = validate_url("ab")
        self.assertFalse(valid)

    def test_invalid_ftp_scheme(self):
        valid, msg = validate_url("ftp://files.example.com")
        self.assertFalse(valid)

    def test_invalid_no_scheme(self):
        valid, msg = validate_url("google.com")
        self.assertFalse(valid)


class TestFeatureExtraction(unittest.TestCase):

    def test_extract_features_https_safe(self):
        url = "https://www.google.com"
        features, vector = extract_features(url)

        self.assertTrue(features["is_https"])
        self.assertFalse(features["has_ip"])
        self.assertFalse(features["has_sensitive"])
        self.assertEqual(len(vector), 14)  # 14-feature vector

    def test_extract_features_phishing_heuristics(self):
        url = "http://192.168.1.100/paypal-login-verify/secure.php"
        features, vector = extract_features(url)

        self.assertFalse(features["is_https"])
        self.assertTrue(features["has_ip"])
        self.assertTrue(features["has_sensitive"])
        self.assertEqual(len(vector), 14)

    def test_extract_features_shortener(self):
        url = "http://bit.ly/secure-login"
        features, _ = extract_features(url)
        self.assertTrue(features["is_shortened"])

    def test_extract_suspicious_tld(self):
        url = "http://bank-login-verify.xyz/auth"
        features, _ = extract_features(url)
        self.assertTrue(features["has_suspicious_tld"])
        self.assertTrue(features["has_dash"])

    def test_extract_known_safe_domain(self):
        url = "https://www.paypal.com/us/home"
        features, _ = extract_features(url)
        self.assertTrue(features["is_known_safe"])


class TestPredictEndpoint(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Start the app lifespan (trains the model) once for all endpoint tests."""
        cls._ctx = TestClient(app, raise_server_exceptions=True)
        cls._ctx.__enter__()
        cls.c = cls._ctx

    @classmethod
    def tearDownClass(cls):
        cls._ctx.__exit__(None, None, None)

    def test_predict_safe_url(self):
        res = self.c.post("/predict", json={"url": "https://www.wikipedia.org", "threshold": 0.5})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data["is_phishing"])
        self.assertEqual(data["risk_level"], "Low")
        self.assertLess(data["probability"], 0.5)

    def test_predict_phishing_url(self):
        res = self.c.post("/predict", json={
            "url": "http://secure-login-bank-verification.com/login.html",
            "threshold": 0.5
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["is_phishing"])
        self.assertEqual(data["risk_level"], "High")
        self.assertGreater(data["probability"], 0.5)

    def test_predict_invalid_url_returns_422(self):
        # 'bhhb' has no TLD — should return HTTP 422
        res = self.c.post("/predict", json={"url": "bhhb", "threshold": 0.5})
        self.assertEqual(res.status_code, 422)
        self.assertIn("detail", res.json())

    def test_predict_bare_word_without_scheme_422(self):
        res = self.c.post("/predict", json={"url": "notaurl", "threshold": 0.5})
        self.assertEqual(res.status_code, 422)

    def test_health_endpoint(self):
        res = self.c.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")

    def test_known_safe_domain_capped(self):
        res = self.c.post("/predict", json={"url": "https://www.google.com", "threshold": 0.5})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        # Known-safe cap means probability must be <= 0.15
        self.assertLessEqual(data["probability"], 0.15)


if __name__ == "__main__":
    unittest.main()
