"""Lark webhook endpoint for bot messages."""

import logging
import json
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.lark_bot import LarkBot
from app.router import Router

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize bot and router
lark_bot = LarkBot()
news_router = Router()


class LarkEvent(BaseModel):
    """Lark event model."""
    schema: Optional[str] = None
    header: Optional[Dict[str, Any]] = None
    event: Optional[Dict[str, Any]] = None


@router.post("/lark/webhook")
async def lark_webhook(request: Request):
    """
    Handle incoming Lark bot events.
    
    Supports:
    - URL verification (required for setup)
    - Message events with @NewsBot mentions
    """
    try:
        body = await request.json()
        logger.debug(f"Received Lark webhook: {body}")

        # URL verification challenge
        if body.get("type") == "url_verification":
            challenge = body.get("challenge")
            logger.info("Lark URL verification challenge received")
            return {"challenge": challenge}

        # Handle message events
        event_type = body.get("header", {}).get("event_type")
        
        if event_type == "im.message.receive_v1":
            await handle_message_event(body)
            return {"code": 0, "msg": "success"}

        logger.warning(f"Unhandled event type: {event_type}")
        return {"code": 0, "msg": "ignored"}

    except Exception as e:
        logger.error(f"Error handling Lark webhook: {e}", exc_info=True)
        return {"code": 1, "msg": str(e)}


async def handle_message_event(event_data: Dict[str, Any]):
    """Handle incoming message event."""
    try:
        # Parse message
        parsed = lark_bot.parse_message(event_data)
        if not parsed:
            logger.warning("Could not parse message")
            return

        # Check if bot is mentioned
        if not lark_bot.is_bot_mentioned(parsed, bot_name="NewsBot"):
            logger.debug("Bot not mentioned, ignoring message")
            return

        # Extract command and category
        command_info = lark_bot.extract_command(parsed["text"])
        category = command_info.get("category")
        
        logger.info(f"Processing news request from user {parsed['user_id']}, category: {category}")

        # Send "processing" message
        message_id = parsed["message_id"]
        chat_id = parsed.get("chat_id")
        lark_bot.send_reply(
            message_id=message_id,
            content="Fetching latest news summary...",
            msg_type="text",
            chat_id=chat_id
        )

        # Run NewsBot
        try:
            result = news_router.handle_news_request(category=category)
            
            if result.get("success") and result.get("summary"):
                # Send full summary as markdown
                summary = result["summary"]
                
                # Format as Lark interactive card
                card_content = {
                    "config": {"wide_screen_mode": True},
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": f"Daily News Summary - {result.get('timestamp', '')[:10]}"
                        }
                    },
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": summary
                        }
                    ]
                }
                
                lark_bot.send_reply(
                    message_id=message_id,
                    content=json.dumps(card_content),
                    msg_type="interactive",
                    chat_id=chat_id
                )
                logger.info("Successfully sent news summary to Lark")
            else:
                # Send error message
                error_msg = result.get("error", "Sorry, couldn't fetch news right now.")
                lark_bot.send_reply(
                    message_id=message_id,
                    content=f"❌ {error_msg}",
                    msg_type="text",
                    chat_id=chat_id
                )

        except Exception as e:
            logger.error(f"Error running NewsBot: {e}", exc_info=True)
            lark_bot.send_reply(
                message_id=message_id,
                content="Sorry, couldn't fetch news right now.",
                msg_type="text",
                chat_id=parsed.get("chat_id")
            )

    except Exception as e:
        logger.error(f"Error handling message event: {e}", exc_info=True)
