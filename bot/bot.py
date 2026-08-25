import asyncio
import logging
import os
import sys
from pathlib import Path

BACK_DIR = Path(__file__).resolve().parent.parent / "back"
if str(BACK_DIR) not in sys.path:
    sys.path.insert(0, str(BACK_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()


from aiogram import Bot, Dispatcher, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from asgiref.sync import sync_to_async
from bot_settings.models import BotConfiguration
from handlers.user import user
from middleware.logging import LoggingMiddleware


def get_active_bot_token():
    config = BotConfiguration.objects.filter(is_active=True).first()
    if config:
        return config.token
    raise ValueError("Активный токен бота не найден в базе данных Django!")


async def main():
    token = await sync_to_async(get_active_bot_token)()
    bot = Bot(token=str(token))
    dp = Dispatcher()
    dp.message.middleware(LoggingMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_routers(user)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
