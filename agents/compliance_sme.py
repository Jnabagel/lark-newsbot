"""ComplianceSME agent for RAG-based compliance queries."""

import logging
from typing import Dict, List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.llm_client import LLMClient
from services.vector_store import VectorStore

logger = logging.getLogger(__name__)


class ComplianceSME:
    """RAG-based compliance knowledge assistant."""

    def __init__(self, vector_store: VectorStore, llm_client: LLMClient):
        """
        Initialize ComplianceSME.

        Args:
            vector_store: Vector store instance
            llm_client: LLM client instance
        """
        self.vector_store = vector_store
        self.llm_client = llm_client
        logger.info("Initialized ComplianceSME")

    def answer(self, question: str) -> Dict:
        """
        Answer a compliance question using RAG.

        Args:
            question: User question

        Returns:
            Dict with 'answer', 'sources', 'confidence', 'disclaimer' keys
        """
        logger.info(f"Processing compliance question: {question[:50]}...")

        try:
            # Retrieve relevant documents
            retrieved_docs = self.vector_store.similarity_search(question, top_k=5)

            if not retrieved_docs:
                logger.warning("No relevant documents found")
                return self._create_fallback_response(question)

            # Build context from retrieved documents
            context_parts = []
            source_names = set()

            for doc in retrieved_docs:
                context_parts.append(f"Document: {doc['document_name']}\n{doc['text']}")
                source_names.add(doc['document_name'])

            context = "\n\n---\n\n".join(context_parts)

            # Generate answer using LLM
            prompt = f"""Based on the following compliance documents, answer the question accurately and concisely.

Documents:
{context}

Question: {question}

Provide a clear, factual answer based only on the provided documents. If the documents don't contain enough information, say so."""

            answer = self.llm_client.generate(
                prompt=prompt,
                temperature=0.3,  # Low temperature for factual responses
                system_prompt="You are a compliance expert assistant. Provide accurate, factual answers based on the provided documents."
            )

            # Calculate confidence (simple heuristic based on retrieval distance)
            avg_distance = sum(doc.get("distance", 1.0) for doc in retrieved_docs) / len(retrieved_docs)
            confidence = "high" if avg_distance < 0.3 else "medium" if avg_distance < 0.6 else "low"

            result = {
                "answer": answer,
                "sources": list(source_names),
                "confidence": confidence,
                "disclaimer": "Internal guidance only. Not legal advice.",
                "retrieved_count": len(retrieved_docs),
            }

            logger.info(f"Generated answer with {len(source_names)} sources")
            return result

        except Exception as e:
            logger.error(f"Error processing question: {e}", exc_info=True)
            return {
                "answer": "I encountered an error processing your question. Please try again.",
                "sources": [],
                "confidence": "none",
                "disclaimer": "Internal guidance only. Not legal advice.",
                "error": str(e),
            }

    def _create_fallback_response(self, question: str) -> Dict:
        """Create fallback response when no documents found."""
        return {
            "answer": "I couldn't find relevant compliance documents to answer your question. Please ensure the knowledge base has been populated with relevant documents.",
            "sources": [],
            "confidence": "none",
            "disclaimer": "Internal guidance only. Not legal advice.",
        }
