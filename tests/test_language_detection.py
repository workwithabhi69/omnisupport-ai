"""
Unit Tests for Multilingual Language Detection.
Tests English, Hindi, Marathi discrimination, empty inputs, and mixed language queries.
"""

import os
import sys
import unittest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ml.language_detection.detector import LanguageDetector


class TestLanguageDetector(unittest.TestCase):
    def setUp(self):
        self.detector = LanguageDetector()

    def test_english_queries(self):
        queries = [
            "How long does delivery take?",
            "How can I return my product?",
            "When will I receive my refund?",
            "Can I cancel my order before dispatch?"
        ]
        for q in queries:
            res = self.detector.detect(q)
            self.assertEqual(res["language"], "en", f"Failed on English query: {q}")
            self.assertGreater(res["confidence"], 0.6)

    def test_hindi_queries(self):
        queries = [
            "डिलीवरी में कितना समय लगता है?",
            "मैं अपना ऑर्डर कैसे वापस कर सकता हूँ?",
            "मेरा रिफंड कब मिलेगा?",
            "क्या मैं ऑर्डर रद्द कर सकता हूँ?"
        ]
        for q in queries:
            res = self.detector.detect(q)
            self.assertEqual(res["language"], "hi", f"Failed on Hindi query: {q}")
            self.assertGreater(res["confidence"], 0.6)

    def test_marathi_queries(self):
        queries = [
            "डिलिव्हरीसाठी किती वेळ लागतो?",
            "मी माझे उत्पादन परत कसे करू शकतो?",
            "मला माझा परतावा कधी मिळेल?",
            "मी माझी ऑर्डर रद्द करू शकतो का?"
        ]
        for q in queries:
            res = self.detector.detect(q)
            self.assertEqual(res["language"], "mr", f"Failed on Marathi query: {q}")
            self.assertGreater(res["confidence"], 0.6)

    def test_empty_and_symbols(self):
        res_empty = self.detector.detect("")
        self.assertEqual(res_empty["language"], "en")
        self.assertEqual(res_empty["confidence"], 0.0)

        res_symbols = self.detector.detect("??? !!! ###")
        self.assertEqual(res_symbols["language"], "en")

    def test_mixed_language_flag(self):
        res_mixed = self.detector.detect("Order नंबर 12345 कधी मिळेल?")
        self.assertTrue(res_mixed["is_mixed"])
        self.assertEqual(res_mixed["language"], "mr")


if __name__ == "__main__":
    unittest.main()
