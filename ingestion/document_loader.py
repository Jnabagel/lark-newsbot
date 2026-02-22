"""Document loading utilities."""

import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Loads documents from local files."""

    @staticmethod
    def load_text_file(file_path: str) -> str:
        """
        Load text content from a file.

        Args:
            file_path: Path to the text file

        Returns:
            File content as string
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            logger.info(f"Loaded document: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}", exc_info=True)
            raise

    @staticmethod
    def load_directory(directory_path: str, extensions: List[str] = None) -> List[Dict[str, str]]:
        """
        Load all text files from a directory.

        Args:
            directory_path: Path to directory
            extensions: List of file extensions to load (default: ['.txt', '.md'])

        Returns:
            List of dicts with keys: 'content', 'file_name', 'file_path'
        """
        if extensions is None:
            extensions = ['.txt', '.md']

        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        documents = []
        for ext in extensions:
            for file_path in directory.rglob(f"*{ext}"):
                try:
                    content = DocumentLoader.load_text_file(str(file_path))
                    documents.append({
                        "content": content,
                        "file_name": file_path.name,
                        "file_path": str(file_path),
                    })
                except Exception as e:
                    logger.warning(f"Skipping file {file_path}: {e}")

        logger.info(f"Loaded {len(documents)} documents from {directory_path}")
        return documents
