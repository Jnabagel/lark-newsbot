"""Router logic for handling requests and calling agents."""

import logging
import time
from typing import Dict
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.llm_client import LLMClient
from services.lark_client import LarkClient
from services.vector_store import VectorStore
from agents.newsbot import NewsBot
from agents.compliance_sme import ComplianceSME

logger = logging.getLogger(__name__)


class Router:
    """Main router for handling requests and delegating to agents."""

    def __init__(self):
        """Initialize router with agent dependencies."""
        self.llm_client = LLMClient()
        self.lark_client = LarkClient()
        self.vector_store = VectorStore()
        
        self.newsbot = NewsBot(self.llm_client, self.lark_client)
        self.compliance_sme = ComplianceSME(self.vector_store, self.llm_client)
        
        logger.info("Initialized Router")

    def handle_news_request(self, category: Optional[str] = None) -> Dict:
        """
        Handle news bot request.

        Returns:
            Response dict
        """
        start_time = time.time()
        logger.info("Handling news request")

        try:
            result = self.newsbot.run(category=category)
            duration = time.time() - start_time
            result["execution_time_seconds"] = duration
            logger.info(f"News request completed in {duration:.2f}s")
            return result
        except Exception as e:
            logger.error(f"Error handling news request: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "execution_time_seconds": time.time() - start_time,
            }

    def handle_compliance_query(self, question: str) -> Dict:
        """
        Handle compliance query.

        Args:
            question: User question

        Returns:
            Response dict
        """
        start_time = time.time()
        logger.info(f"Handling compliance query: {question[:50]}...")

        try:
            result = self.compliance_sme.answer(question)
            duration = time.time() - start_time
            result["execution_time_seconds"] = duration
            logger.info(f"Compliance query completed in {duration:.2f}s")
            return result
        except Exception as e:
            logger.error(f"Error handling compliance query: {e}", exc_info=True)
            return {
                "answer": "An error occurred processing your query.",
                "sources": [],
                "confidence": "none",
                "disclaimer": "Internal guidance only. Not legal advice.",
                "error": str(e),
                "execution_time_seconds": time.time() - start_time,
            }
