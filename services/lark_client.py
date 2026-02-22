"""Lark webhook client for sending messages."""

import logging
from typing import Optional
import httpx

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings

logger = logging.getLogger(__name__)


class LarkClient:
    """Client for sending messages to Lark via webhook."""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Lark client.

        Args:
            webhook_url: Lark webhook URL (defaults to settings)
        """
        self.webhook_url = webhook_url or settings.lark_webhook_url
        if not self.webhook_url:
            raise ValueError("LARK_WEBHOOK_URL is required")
        logger.info("Initialized Lark client")

    def send_message(self, content: str, title: Optional[str] = None) -> bool:
        """
        Send a text message to Lark.

        Args:
            content: Message content
            title: Optional message title

        Returns:
            True if successful, False otherwise
        """
        try:
            # Lark webhook expects JSON format
            payload = {
                "msg_type": "text",
                "content": {
                    "text": content
                }
            }

            if title:
                payload["content"]["text"] = f"{title}\n\n{content}"

            response = httpx.post(
                self.webhook_url,
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()

            logger.info("Successfully sent message to Lark")
            return True

        except Exception as e:
            logger.error(f"Failed to send message to Lark: {e}", exc_info=True)
            return False

    def send_markdown(self, content: str, title: Optional[str] = None) -> bool:
        """
        Send a markdown message to Lark.

        Args:
            content: Markdown content
            title: Optional message title

        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                "msg_type": "interactive",
                "card": {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": title or "Notification"
                        }
                    },
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": content
                        }
                    ]
                }
            }

            response = httpx.post(
                self.webhook_url,
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()

            logger.info("Successfully sent markdown message to Lark")
            return True

        except Exception as e:
            logger.error(f"Failed to send markdown message to Lark: {e}", exc_info=True)
            return False
