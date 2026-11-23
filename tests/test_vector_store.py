"""
Integration Tests for ChromaDB Vector Store & Multilingual Semantic Retrieval.
"""

import os
import sys
import unittest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ml.retrieval.vector_store import VectorStoreManager


class TestVectorStore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vsm = VectorStoreManager()

    def test_collection_has_documents(self):
        count = self.vsm.get_total_chunks()
        self.assertGreater(count, 0, "Vector store should contain indexed knowledge base chunks.")

    def test_semantic_search_english(self):
        results = self.vsm.search("How long does delivery take?", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertIn("shipping", results[0]["metadata"]["source"].lower())

    def test_semantic_search_hindi(self):
        results = self.vsm.search("डिलीवरी में कितना समय लगता है?", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertIn("shipping", results[0]["metadata"]["source"].lower())

    def test_semantic_search_marathi(self):
        results = self.vsm.search("डिलिव्हरीसाठी किती वेळ लागतो?", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertIn("shipping", results[0]["metadata"]["source"].lower())

    def test_list_indexed_documents(self):
        summary = self.vsm.list_indexed_documents()
        self.assertGreater(len(summary), 0)
        self.assertTrue(any("shipping" in s["source"].lower() for s in summary))


if __name__ == "__main__":
    unittest.main()
