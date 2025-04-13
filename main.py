import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from news_ann import schedule_ann_news

API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = YOUR_CHAT_ID  # Your personal/group/channel chat ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

async def on_startup(_):
    # Schedule the news fetch and post job
    schedule_ann_news(scheduler, bot, CHAT_ID)
    scheduler.start()
    logging.info("Bot started and scheduler running")

if __name__ == "__main__":
    # Setup logging for better debugging
    logging.basicConfig(level=logging.INFO)

    # Start polling with custom startup logic
    executor.start_polling(dp, on_startup=on_startup)
