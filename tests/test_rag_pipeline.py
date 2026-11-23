"""
System and Integration Tests for Multilingual RAG Pipeline.
Verifies grounded response generation, fallback when LLM is unavailable, and out-of-scope handling.
"""

import os
import sys
import unittest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ml.rag.rag_pipeline import MultilingualRAGPipeline


class TestRAGPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = MultilingualRAGPipeline()

    def test_english_query_grounding(self):
        res = self.pipeline.answer_query("How long does standard delivery take?", use_llm=False)
        self.assertEqual(res["language"], "en")
        self.assertGreater(len(res["sources"]), 0)
        self.assertIn("3 to 5", res["answer"])

    def test_hindi_query_grounding(self):
        res = self.pipeline.answer_query("मेरा रिफंड कब मिलेगा?", use_llm=False)
        self.assertEqual(res["language"], "hi")
        self.assertGreater(len(res["sources"]), 0)
        self.assertTrue("24 से 48" in res["answer"] or "रिफंड" in res["answer"])

    def test_marathi_query_grounding(self):
        res = self.pipeline.answer_query("डिलिव्हरीसाठी किती वेळ लागतो?", use_llm=False)
        self.assertEqual(res["language"], "mr")
        self.assertGreater(len(res["sources"]), 0)
        self.assertTrue("3 ते 5" in res["answer"] or "डिलिव्हरी" in res["answer"])

    def test_unsupported_out_of_scope_query(self):
        res = self.pipeline.answer_query("What is the recipe for chocolate cake?", similarity_threshold=0.82)
        self.assertEqual(res["generation_mode"], "out_of_scope")
        self.assertEqual(len(res["sources"]), 0)
        self.assertIn("could not find relevant information", res["answer"].lower())

    def test_manual_language_override(self):
        res = self.pipeline.answer_query("How long does delivery take?", manual_language="hi", use_llm=False)
        self.assertEqual(res["language"], "hi")


if __name__ == "__main__":
    unittest.main()
