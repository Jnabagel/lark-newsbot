"""Vector store service using ChromaDB."""

import logging
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB-based vector store for document storage and retrieval."""

    def __init__(self, collection_name: str = "compliance_docs"):
        """
        Initialize vector store.

        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.collection_name = collection_name
        self.embedding_service = EmbeddingService()
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Initialized vector store with collection: {collection_name}")

    def add_documents(self, documents: List[Dict[str, str]]) -> None:
        """
        Add documents to the vector store.

        Args:
            documents: List of dicts with keys:
                - text: chunk text
                - document_name: source document name
                - metadata: optional additional metadata dict
        """
        if not documents:
            logger.warning("No documents to add")
            return

        texts = [doc["text"] for doc in documents]
        document_names = [doc["document_name"] for doc in documents]
        metadatas = []
        ids = []

        # Generate embeddings
        embeddings = self.embedding_service.generate_embeddings(texts)

        # Prepare metadata and IDs
        for i, doc in enumerate(documents):
            metadata = {
                "document_name": document_names[i],
                "timestamp": doc.get("timestamp", ""),
            }
            if "metadata" in doc and isinstance(doc["metadata"], dict):
                metadata.update(doc["metadata"])
            metadatas.append(metadata)
            ids.append(f"{document_names[i]}_{i}")

        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"Added {len(documents)} documents to vector store")

    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents.

        Args:
            query: Query text
            top_k: Number of results to return

        Returns:
            List of dicts with keys: text, document_name, metadata, distance
        """
        if self.collection.count() == 0:
            logger.warning("Vector store is empty")
            return []

        # Generate query embedding
        query_embedding = self.embedding_service.generate_embeddings([query])[0]

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Format results
        formatted_results = []
        if results["documents"] and len(results["documents"][0]) > 0:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "text": results["documents"][0][i],
                    "document_name": results["metadatas"][0][i].get("document_name", "unknown"),
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results["distances"] else None,
                })

        logger.info(f"Found {len(formatted_results)} results for query")
        return formatted_results

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
        }
