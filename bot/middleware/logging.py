import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = event.from_user
        username = f"@{user.username}" if user.username else f"id:{user.id}"
        chat_type = type(event.chat).__name__ if hasattr(event, "chat") else "?"
        text = (event.text or event.caption or "[media]")[:80]

        logger.info(
            "📨 %-25s │ %-12s │ %s",
            username,
            chat_type,
            text,
        )

        return await handler(event, data)
