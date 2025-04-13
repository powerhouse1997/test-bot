import logging
import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers.anime import router as anime_router
from handlers.manga import router as manga_router
from handlers.character import router as character_router
from handlers.season import router as season_router
from handlers.top import router as top_router
from handlers.news import router as news_router
from news import send_daily_news  # Import the scheduled news sender

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize bot
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Initialize dispatcher with the bot instance
dp = Dispatcher()

# Register all routers
dp.include_router(anime_router)
dp.include_router(manga_router)
dp.include_router(character_router)
dp.include_router(season_router)
dp.include_router(top_router)
dp.include_router(news_router)

# Entry point
async def main():
    logging.basicConfig(level=logging.INFO)

    # Start scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_daily_news, "interval", hours=24, args=[bot])
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
