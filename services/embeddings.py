"""Embedding generation service."""

import logging
from typing import List, Optional
from openai import OpenAI

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize embedding service.

        Args:
            api_key: OpenAI API key (defaults to settings)
        """
        api_key = api_key or settings.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for embeddings")
        self.client = OpenAI(api_key=api_key)
        self.model = settings.embedding_model
        logger.info(f"Initialized embedding service with model: {self.model}")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Embedding generation error: {e}", exc_info=True)
            raise

