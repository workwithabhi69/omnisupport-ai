"""
Unit Tests for Multilingual Sentiment Analysis, Information Extraction, and DB Persistence.
Covers Assessment Rubric Criterion 2 (CO2 - 8 Marks).
"""

import os
import sys
import unittest
import tempfile

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ml.sentiment_extraction.analyzer import CustomerQueryAnalyzer
from backend.database.sqlite_db import SQLiteManager


class TestSentimentAndExtraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = CustomerQueryAnalyzer()

    def test_english_positive_sentiment(self):
        res = self.analyzer.analyze_sentiment("The delivery was great and very fast, thank you!")
        self.assertEqual(res["sentiment"], "Positive")
        self.assertGreater(res["polarity"], 0.0)
        self.assertIn("Positive", res["badge"])

    def test_hindi_negative_urgent_sentiment(self):
        res = self.analyzer.analyze_sentiment("मेरा पार्सल खराब और टूटा हुआ मिला, तुरंत मदद करें!")
        self.assertEqual(res["sentiment"], "Negative")
        self.assertTrue(res["is_urgent"])
        self.assertLess(res["polarity"], 0.0)

    def test_marathi_intent_and_entity_extraction(self):
        res = self.analyzer.process_query("माझे ₹500 परतावा 3 दिवसात मिळेल का? ऑर्डर #9821")
        info = res["information"]
        self.assertEqual(info["intent"], "Refund Status")
        self.assertIn("₹500", info["extracted_currency_amounts"])
        self.assertIn("#9821", info["extracted_order_ids"])
        self.assertTrue(any("3" in t for t in info["extracted_timelines"]))

    def test_delivery_intent_classification(self):
        res = self.analyzer.extract_information("How long does standard delivery take?")
        self.assertEqual(res["intent"], "Delivery Inquiry")

    def test_sqlite_persistence_of_sentiment_and_intent(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_db_path = f.name

        try:
            db = SQLiteManager(db_path=temp_db_path)
            session_id = "test_sess_001"
            db.get_or_create_session(session_id, username="customer")

            # Add user message with sentiment & intent
            analysis = self.analyzer.process_query("I am very angry, refund my ₹999 immediately!")
            db.add_message(
                session_id=session_id,
                role="user",
                content="I am very angry, refund my ₹999 immediately!",
                language="en",
                sentiment=analysis["sentiment"],
                extracted_info=analysis["information"]
            )

            # Retrieve messages from DB
            messages = db.get_session_messages(session_id)
            self.assertEqual(len(messages), 1)
            msg = messages[0]
            self.assertIsNotNone(msg.get("sentiment"))
            self.assertEqual(msg["sentiment"]["sentiment"], "Negative")
            self.assertTrue(msg["sentiment"]["is_urgent"])
            self.assertIsNotNone(msg.get("extracted_info"))
            self.assertEqual(msg["extracted_info"]["intent"], "Refund Status")
            self.assertIn("₹999", msg["extracted_info"]["extracted_currency_amounts"])
        finally:
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)


if __name__ == "__main__":
    unittest.main()
