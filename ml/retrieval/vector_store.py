"""
ChromaDB Vector Store Manager for Multilingual Knowledge Base.
Handles persistent vector indexing, semantic search, document deletion, and collection metadata.
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from ml.embeddings.embedder import MultilingualEmbedder


class VectorStoreManager:
    DEFAULT_COLLECTION = "ecommerce_knowledge_base"

    def __init__(
        self,
        persist_directory: str = None,
        embedder: Optional[MultilingualEmbedder] = None,
        collection_name: str = DEFAULT_COLLECTION
    ):
        if persist_directory is None:
            # Default to vector_store in project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            persist_directory = os.path.join(base_dir, "vector_store")

        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)

        self.embedder = embedder or MultilingualEmbedder()
        self.collection_name = collection_name

        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Multilingual E-commerce Policies Knowledge Base", "hnsw:space": "cosine"}
        )

    def add_documents(
        self,
        chunks: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> int:
        """
        Embeds and indexes document chunks into ChromaDB.
        """
        if not chunks:
            return 0

        if ids is None:
            import uuid
            ids = [f"chunk_{uuid.uuid4().hex[:10]}_{i}" for i in range(len(chunks))]

        # Generate embeddings
        embeddings = self.embedder.embed_documents(chunks)

        # ChromaDB accepts add in batches
        batch_size = 64
        for i in range(0, len(chunks), batch_size):
            end_idx = min(i + batch_size, len(chunks))
            self.collection.add(
                documents=chunks[i:end_idx],
                embeddings=embeddings[i:end_idx],
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )

        return len(chunks)

    def search(
        self,
        query: str,
        top_k: int = 4,
        filter_metadata: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.30
    ) -> List[Dict[str, Any]]:
        """
        Performs semantic vector search against ChromaDB.
        Returns top-K relevant chunks with cosine similarity and metadata.
        """
        if not query or not query.strip():
            return []

        query_embedding = self.embedder.embed_query(query)
        
        query_kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, max(1, self.collection.count())),
            "include": ["documents", "metadatas", "distances"]
        }
        if filter_metadata:
            query_kwargs["where"] = filter_metadata

        if self.collection.count() == 0:
            return []

        results = self.collection.query(**query_kwargs)

        retrieved_items = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
            distances = results["distances"][0] if results["distances"] else [1.0] * len(docs)
            doc_ids = results["ids"][0] if results["ids"] else [""] * len(docs)

            for doc, meta, dist, cid in zip(docs, metas, distances, doc_ids):
                # Cosine distance: similarity = 1 - distance
                similarity = max(0.0, 1.0 - dist)
                if similarity >= score_threshold:
                    retrieved_items.append({
                        "id": cid,
                        "content": doc,
                        "metadata": meta,
                        "distance": round(dist, 4),
                        "similarity": round(similarity, 4)
                    })

        # Sort descending by similarity
        retrieved_items.sort(key=lambda x: x["similarity"], reverse=True)
        return retrieved_items

    def delete_by_source(self, source_name: str) -> int:
        """Deletes all chunks belonging to a specific source document."""
        current = self.collection.get(where={"source": source_name})
        if current and current["ids"]:
            count = len(current["ids"])
            self.collection.delete(ids=current["ids"])
            return count
        return 0

    def list_indexed_documents(self) -> List[Dict[str, Any]]:
        """Summarizes all indexed files in the vector database."""
        all_data = self.collection.get(include=["metadatas"])
        if not all_data or not all_data["metadatas"]:
            return []

        sources: Dict[str, Dict[str, Any]] = {}
        for meta in all_data["metadatas"]:
            src = meta.get("source", "Unknown")
            lang = meta.get("language", "unknown")
            cat = meta.get("category", "General")
            
            if src not in sources:
                sources[src] = {
                    "source": src,
                    "languages": set(),
                    "categories": set(),
                    "chunk_count": 0
                }
            sources[src]["languages"].add(lang)
            sources[src]["categories"].add(cat)
            sources[src]["chunk_count"] += 1

        summary = []
        for src, info in sources.items():
            summary.append({
                "source": src,
                "languages": list(info["languages"]),
                "categories": list(info["categories"]),
                "chunk_count": info["chunk_count"]
            })
        return summary

    def get_total_chunks(self) -> int:
        return self.collection.count()

    def reset(self):
        """Resets the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Multilingual E-commerce Policies Knowledge Base", "hnsw:space": "cosine"}
        )
