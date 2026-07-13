"""
Sentinel AI - RAG (Retrieval-Augmented Generation) Service
=============================================================
File: backend/services/rag_service.py
Purpose: Integrates Google GenAI embeddings and vector search to provide
         RAG capabilities for case files, standard operating procedures,
         and historical reports.

Dependencies: google-genai, lancedb, numpy, loguru
"""

import os
from typing import Any
from loguru import logger
import lancedb
from google import genai
from google.genai import types

from backend.config.settings import get_settings
from backend.config.config import PROJECT_ROOT

settings = get_settings()


class RAGService:
    """Service for Retrieval-Augmented Generation using LanceDB and Gemini Embeddings."""

    def __init__(self) -> None:
        """Initialize LanceDB and Gemini Embedding client."""
        self.api_key = settings.GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        
        # LanceDB setup for vector storage
        db_path = PROJECT_ROOT / "data" / "lancedb"
        os.makedirs(db_path, exist_ok=True)
        self.db = lancedb.connect(str(db_path))
        self.table_name = "sentinel_knowledge_base"
        
        # The embedding model to use
        self.embedding_model = "text-embedding-004"

    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding vector for text using Gemini.
        """
        if not self.client:
            logger.warning("RAG: Gemini client not initialized. Using dummy embedding.")
            return [0.0] * 768
            
        try:
            response = await self.client.aio.models.embed_content(
                model=self.embedding_model,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type=types.TaskType.RETRIEVAL_DOCUMENT
                )
            )
            return response.embeddings[0].values
        except Exception as exc:
            logger.error(f"Error generating embedding: {str(exc)}")
            raise

    async def similarity_search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """
        Search for similar documents in the knowledge base.
        """
        try:
            # Check if table exists
            if self.table_name not in self.db.table_names():
                logger.warning(f"RAG table '{self.table_name}' does not exist.")
                return []
                
            table = self.db.open_table(self.table_name)
            
            # Generate query embedding
            query_config = types.EmbedContentConfig(task_type=types.TaskType.RETRIEVAL_QUERY)
            response = await self.client.aio.models.embed_content(
                model=self.embedding_model,
                contents=query,
                config=query_config
            )
            query_embedding = response.embeddings[0].values
            
            # Perform vector search
            results = table.search(query_embedding).limit(limit).to_list()
            return results
            
        except Exception as exc:
            logger.error(f"Error during RAG similarity search: {str(exc)}")
            return []

    async def build_context(self, query: str, limit: int = 3) -> str:
        """
        Retrieve relevant documents and format them as context for LLM prompts.
        """
        results = await self.similarity_search(query, limit)
        
        if not results:
            return "No relevant context found in knowledge base."
            
        context_parts = []
        for i, res in enumerate(results):
            score = 1.0 - res.get('_distance', 0)
            doc_id = res.get('doc_id', 'Unknown')
            text = res.get('text', '')
            context_parts.append(f"[Document {i+1} | Source: {doc_id} | Relevance: {score:.2f}]\n{text}\n")
            
        return "\n".join(context_parts)
