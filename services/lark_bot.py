"""Lark bot service for receiving and responding to messages."""

import logging
import json
import time
import httpx
from typing import Optional, Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings

logger = logging.getLogger(__name__)


class LarkBot:
    """Lark bot for receiving messages and sending replies."""

    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None):
        """
        Initialize Lark bot.

        Args:
            app_id: Lark app ID (defaults to settings)
            app_secret: Lark app secret (defaults to settings)
        """
        self.app_id = app_id or settings.lark_app_id
        self.app_secret = app_secret or settings.lark_app_secret
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        logger.info("Initialized LarkBot")

    def _get_access_token(self) -> str:
        """
        Get or refresh access token.

        Returns:
            Access token string
        """
        # Return cached token if still valid
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        if not self.app_id or not self.app_secret:
            raise ValueError("Lark app_id and app_secret are required for bot functionality")

        try:
            url = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
            payload = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }

            response = httpx.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            if data.get("code") == 0:
                self._access_token = data["tenant_access_token"]
                # Token expires in 2 hours, refresh 5 minutes early
                self._token_expires_at = time.time() + (data.get("expire", 7200) - 300)
                logger.info("Obtained Lark access token")
                return self._access_token
            else:
                raise Exception(f"Failed to get access token: {data.get('msg')}")

        except Exception as e:
            logger.error(f"Error getting Lark access token: {e}", exc_info=True)
            raise

    def send_reply(self, message_id: str, content: str, msg_type: str = "text", chat_id: Optional[str] = None) -> bool:
        """
        Reply to a message in Lark.

        Args:
            message_id: ID of the message to reply to
            content: Reply content
            msg_type: Message type ('text' or 'interactive' for markdown)
            chat_id: Chat ID (optional, will use message_id if not provided)

        Returns:
            True if successful
        """
        try:
            token = self._get_access_token()
            receive_id = chat_id or message_id
            receive_id_type = "chat_id" if chat_id else "message_id"
            
            url = f"https://open.larksuite.com/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            if msg_type == "interactive":
                # Parse content as JSON if it's markdown
                try:
                    card_content = json.loads(content) if isinstance(content, str) else content
                except:
                    # If not JSON, wrap in card format
                    card_content = {
                        "config": {"wide_screen_mode": True},
                        "elements": [{"tag": "markdown", "content": content}]
                    }
                
                payload = {
                    "receive_id": receive_id,
                    "msg_type": "interactive",
                    "content": json.dumps(card_content)
                }
            else:
                payload = {
                    "receive_id": receive_id,
                    "msg_type": "text",
                    "content": json.dumps({"text": content})
                }

            response = httpx.post(url, headers=headers, json=payload, timeout=10.0)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                logger.info("Successfully sent reply to Lark")
                return True
            else:
                logger.error(f"Failed to send reply: {result.get('msg')}")
                return False

        except Exception as e:
            logger.error(f"Error sending reply to Lark: {e}", exc_info=True)
            return False

    def parse_message(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse incoming message event.

        Args:
            event_data: Lark event data

        Returns:
            Parsed message dict with 'text', 'message_id', 'user_id', 'chat_id' or None
        """
        try:
            event = event_data.get("event", {})
            message = event.get("message", {})
            
            if not message:
                return None

            message_id = message.get("message_id")
            content = message.get("content", "")
            
            # Parse content JSON
            try:
                content_obj = json.loads(content)
                text = content_obj.get("text", "")
            except:
                text = content

            mentions = event.get("mentions", [])
            
            return {
                "text": text,
                "message_id": message_id,
                "user_id": event.get("sender", {}).get("sender_id", {}).get("user_id"),
                "chat_id": event.get("message", {}).get("chat_id"),
                "mentions": mentions,
            }

        except Exception as e:
            logger.error(f"Error parsing message: {e}", exc_info=True)
            return None

    def is_bot_mentioned(self, parsed_message: Dict[str, Any], bot_name: str = "NewsBot") -> bool:
        """
        Check if bot is mentioned in the message.

        Args:
            parsed_message: Parsed message dict
            bot_name: Bot name to check for

        Returns:
            True if bot is mentioned
        """
        text = parsed_message.get("text", "").lower()
        mentions = parsed_message.get("mentions", [])
        
        # Check for @bot_name or mentions
        return (
            f"@{bot_name.lower()}" in text or
            bot_name.lower() in text or
            len(mentions) > 0  # Any mention triggers
        )

    def extract_command(self, text: str) -> Dict[str, Any]:
        """
        Extract command and category from message text.

        Args:
            text: Message text

        Returns:
            Dict with 'command' and 'category' keys
        """
        text_lower = text.lower()
        
        # Remove @mentions and clean up
        import re
        text_clean = re.sub(r'@\w+\s*', '', text_lower).strip()
        
        # Check for commands
        commands = ["news", "summary", "headlines"]
        command = None
        for cmd in commands:
            if cmd in text_clean:
                command = cmd
                break
        
        # Extract category if present
        categories = {
            "business": ["business", "finance", "economy", "market"],
            "technology": ["tech", "technology", "ai", "software"],
            "world": ["world", "global", "international"],
            "sports": ["sports", "sport"],
            "entertainment": ["entertainment", "entertain"],
            "health": ["health", "medical"],
            "science": ["science", "scientific"],
        }
        
        category = None
        for cat, keywords in categories.items():
            if any(keyword in text_clean for keyword in keywords):
                category = cat
                break
        
        return {
            "command": command or "news",  # Default to 'news'
            "category": category
        }
