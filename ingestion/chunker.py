"""Text chunking utilities."""

import logging
from typing import List
import tiktoken

logger = logging.getLogger(__name__)


class Chunker:
    """Chunks text into smaller pieces for vector storage."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, encoding_name: str = "cl100k_base"):
        """
        Initialize chunker.

        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
            encoding_name: Tokenizer encoding name
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)
        logger.info(f"Initialized chunker: chunk_size={chunk_size}, overlap={chunk_overlap}")

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        if not text.strip():
            return []

        # Tokenize text
        tokens = self.encoding.encode(text)

        if len(tokens) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(tokens):
            # Get chunk
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            
            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)

            # Move start position with overlap
            start = end - self.chunk_overlap

        logger.info(f"Chunked text into {len(chunks)} chunks")
        return chunks

    def chunk_documents(self, documents: List[dict]) -> List[dict]:
        """
        Chunk a list of documents.

        Args:
            documents: List of dicts with 'content' and 'file_name' keys

        Returns:
            List of chunk dicts with 'text', 'document_name', 'chunk_index' keys
        """
        all_chunks = []

        for doc in documents:
            content = doc.get("content", "")
            file_name = doc.get("file_name", "unknown")

            chunks = self.chunk_text(content)

            for i, chunk_text in enumerate(chunks):
                all_chunks.append({
                    "text": chunk_text,
                    "document_name": file_name,
                    "chunk_index": i,
                    "metadata": {
                        "total_chunks": len(chunks),
                        "file_path": doc.get("file_path", ""),
                    }
                })

        logger.info(f"Chunked {len(documents)} documents into {len(all_chunks)} chunks")
        return all_chunks
