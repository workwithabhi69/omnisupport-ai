"""
Initializes ChromaDB vector store with default multilingual knowledge base documents.
"""

import os
import sys
import glob

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.services.document_processor import DocumentProcessor
from ml.retrieval.vector_store import VectorStoreManager


def initialize_knowledge_base(reset: bool = False) -> int:
    dp = DocumentProcessor(chunk_size=400, chunk_overlap=60)
    vsm = VectorStoreManager()
    
    if reset:
        vsm.reset()
    elif vsm.get_total_chunks() > 0:
        print(f"Vector store already contains {vsm.get_total_chunks()} chunks.")
        return vsm.get_total_chunks()

    kb_dir = os.path.join(project_root, "data", "knowledge_base")
    files = glob.glob(os.path.join(kb_dir, "*.txt"))
    
    total_indexed = 0
    for f in files:
        fn = os.path.basename(f)
        processed = dp.process_file(fn, f)
        if processed.get("chunks"):
            count = vsm.add_documents(processed["chunks"], processed["metadatas"])
            total_indexed += count
            print(f"Indexed {fn}: {count} chunks (lang={processed['language']}, cat={processed['category']})")

    print(f"\nSuccessfully indexed {total_indexed} chunks into ChromaDB.")
    return total_indexed


if __name__ == "__main__":
    initialize_knowledge_base(reset=True)
