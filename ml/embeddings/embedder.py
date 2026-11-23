"""
Multilingual Embedding Manager using SentenceTransformers.
Supports:
- intfloat/multilingual-e5-small (Default, 384-dim, lightweight & high accuracy)
- BGE-M3 (Configurable alternative)
- Automatic E5 query/passage prefixing for asymmetric semantic search
- Offline snapshot resolver for instant local loading
"""

import os
import glob
from typing import List, Union
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False


class MultilingualEmbedder:
    def __init__(self, model_name: str = "intfloat/multilingual-e5-small"):
        self.model_name = model_name
        self._model = None
        self.is_e5 = "e5" in model_name.lower()

    def _resolve_local_path(self, model_name: str) -> str:
        """Checks if the model is cached in HuggingFace hub snapshots to load 100% offline."""
        # If it's already an existing directory path, return it directly
        if os.path.isdir(model_name):
            return model_name
            
        repo_id = model_name.replace("/", "--")
        cache_dir = os.path.expanduser(f"~/.cache/huggingface/hub/models--{repo_id}/snapshots")
        if os.path.isdir(cache_dir):
            snapshots = glob.glob(os.path.join(cache_dir, "*"))
            if snapshots and os.path.isdir(snapshots[0]):
                return snapshots[0]
        return model_name

    @property
    def model(self):
        if self._model is None:
            if not ST_AVAILABLE:
                raise ImportError("sentence-transformers is required for MultilingualEmbedder")
            
            resolved_path = self._resolve_local_path(self.model_name)
            try:
                self._model = SentenceTransformer(resolved_path)
            except Exception:
                # Fallback to direct model name
                self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for document chunks.
        Adds 'passage: ' prefix if using E5 models.
        """
        if not texts:
            return []
        
        prefixed_texts = [f"passage: {t}" if self.is_e5 else t for t in texts]
        embeddings = self.model.encode(prefixed_texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Generates embedding for a single user query.
        Adds 'query: ' prefix if using E5 models.
        """
        prefixed_query = f"query: {query}" if self.is_e5 else query
        embedding = self.model.encode(prefixed_query, normalize_embeddings=True, show_progress_bar=False)
        return embedding.tolist()

    @property
    def embedding_dim(self) -> int:
        return self.model.get_sentence_embedding_dimension()
