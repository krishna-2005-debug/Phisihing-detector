import unittest
from main import extract_features, predict, URLRequest, train_model

class TestPhishingDetector(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Force-train model before running tests
        train_model()

    def test_extract_features_https_safe(self):
        url = "https://www.google.com"
        features, vector = extract_features(url)
        
        self.assertTrue(features["is_https"])
        self.assertFalse(features["has_ip"])
        self.assertFalse(features["has_sensitive"])
        self.assertEqual(features["subdomain_depth"], 2) # www.google.com
        self.assertEqual(vector[0], len(url))

    def test_extract_features_phishing_heuristics(self):
        url = "http://192.168.1.100/paypal-login-verify/secure.php"
        features, vector = extract_features(url)
        
        self.assertFalse(features["is_https"])
        self.assertTrue(features["has_ip"])
        self.assertTrue(features["has_sensitive"])
        self.assertTrue(features["subdomain_depth"] >= 1)

    def test_extract_features_shortener(self):
        url = "https://bit.ly/secure-login"
        features, _ = extract_features(url)
        self.assertTrue(features["is_shortened"])

    def test_predict_safe_url(self):
        req = URLRequest(url="https://www.wikipedia.org", threshold=0.5)
        res = predict(req)
        
        self.assertEqual(res["url"], req.url)
        self.assertFalse(res["is_phishing"])
        self.assertEqual(res["risk_level"], "Low")
        self.assertTrue(res["probability"] < 0.5)

    def test_predict_phishing_url(self):
        req = URLRequest(url="http://secure-login-bank-verification.com/login.html", threshold=0.5)
        res = predict(req)
        
        self.assertEqual(res["url"], req.url)
        self.assertTrue(res["is_phishing"])
        self.assertEqual(res["risk_level"], "High")
        self.assertTrue(res["probability"] > 0.5)

if __name__ == "__main__":
    unittest.main()
