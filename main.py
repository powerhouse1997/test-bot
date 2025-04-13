import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from news_ann import schedule_ann_news
import os

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')  
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

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

    # Start polling directly using the Dispatcher
    dp.start_polling(on_startup=on_startup)
