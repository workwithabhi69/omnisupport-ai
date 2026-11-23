"""
Tests for Quantitative Evaluation Pipeline.
"""

import os
import sys
import unittest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ml.evaluation.evaluator import ModelEvaluator


class TestEvaluation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evaluator = ModelEvaluator()

    def test_language_detection_benchmark(self):
        res = self.evaluator.evaluate_language_detection()
        self.assertGreaterEqual(res["accuracy"], 0.90)
        self.assertIn("en", res["per_language"])
        self.assertIn("hi", res["per_language"])
        self.assertIn("mr", res["per_language"])

    def test_retrieval_benchmark(self):
        res = self.evaluator.evaluate_retrieval(top_k=3)
        self.assertGreaterEqual(res["recall_at_k"], 0.80)
        self.assertGreaterEqual(res["mean_reciprocal_rank"], 0.80)

    def test_end_to_end_benchmark(self):
        res = self.evaluator.evaluate_end_to_end(use_llm=False)
        self.assertEqual(res["success_rate"], 1.0)
        self.assertEqual(res["error_rate"], 0.0)
        self.assertLess(res["avg_latency_sec"], 1.0)

    def test_sentiment_and_extraction_benchmark(self):
        res = self.evaluator.evaluate_sentiment_and_extraction()
        self.assertGreaterEqual(res["intent_classification_accuracy"], 0.80)
        self.assertIn("Neutral", res["sentiment_distribution"])
        self.assertEqual(res["rubric_mapping"], "CO2 (8 Marks)")


if __name__ == "__main__":
    unittest.main()
