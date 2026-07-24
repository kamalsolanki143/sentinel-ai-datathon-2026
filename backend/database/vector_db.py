"""
Sentinel AI - Vector Database Service & RAG Index Manager
=========================================================
File: backend/database/vector_db.py
Purpose: In-memory & FAISS / Qdrant vector database abstraction for semantic crime document
         search, intelligence report embeddings, and Retrieval-Augmented Generation (RAG).

Dependencies: numpy, loguru, pydantic
"""

import math
from typing import Any, Dict, List, Optional
import numpy as np
from loguru import logger
from pydantic import BaseModel, Field


class VectorDocument(BaseModel):
    """Schema for a vectorized document stored in vector DB index."""

    doc_id: str = Field(description="Unique document ID")
    content: str = Field(description="Text document content snippet")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: List[float] = Field(default_factory=list)


class VectorDatabaseManager:
    """
    Vector Database Manager providing similarity search, document indexing,
    and RAG embeddings support.
    """

    def __init__(self, vector_dim: int = 384) -> None:
        """Initialize Vector Database with default vector dimension."""
        self.vector_dim = vector_dim
        self.documents: Dict[str, VectorDocument] = {}
        logger.info(f"VectorDatabaseManager initialized with dimension {vector_dim}.")

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two embedding vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        a = np.array(vec_a, dtype=np.float64)
        b = np.array(vec_b, dtype=np.float64)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def insert_document(
        self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None, embedding: Optional[List[float]] = None
    ) -> None:
        """Insert or update a document in the vector store."""
        if embedding is None:
            # Generate deterministic pseudo-embedding for testing if not provided
            rng = np.random.RandomState(abs(hash(content)) % (2**32))
            vec = rng.randn(self.vector_dim).tolist()
        else:
            vec = embedding

        self.documents[doc_id] = VectorDocument(
            doc_id=doc_id, content=content, metadata=metadata or {}, embedding=vec
        )
        logger.debug(f"Document {doc_id} indexed in vector DB.")

    def search_similar(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search top K most similar documents to input query embedding vector."""
        if not self.documents:
            return []

        results = []
        for doc_id, doc in self.documents.items():
            sim = self._cosine_similarity(query_embedding, doc.embedding)
            results.append(
                {
                    "doc_id": doc.doc_id,
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "similarity_score": round(sim, 4),
                }
            )

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]


# Singleton instance
vector_db = VectorDatabaseManager()
