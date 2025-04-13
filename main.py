# main.py
from aiogram import Bot, Dispatcher, F
from aiogram.types import BotCommand
from aiogram.client.session import aiohttp
from aiogram.filters import Command
from aiogram import Dispatcher
from aiogram import types
from aiogram import __version__ as aiogram_version
from aiogram.types import ParseMode
from aiogram import types
from aiogram import Bot

API_TOKEN = "TELEGRAM_BOT_TOKEN"
CHAT_ID = CHAT_ID  # Your personal/group/channel chat ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

async def on_startup(_):
    schedule_ann_news(scheduler, bot, CHAT_ID)
    scheduler.start()
    logging.info("Bot started and scheduler running")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_polling(dp, on_startup=on_startup)
