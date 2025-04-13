import logging
import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from handlers.anime import router as anime_router
from handlers.manga import router as manga_router
from handlers.character import router as character_router
from handlers.season import router as season_router
from handlers.top import router as top_router
from handlers.news import router as news_router

from jikan_api import fetch_anime_news  # Your news fetcher

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("YOUR_CHAT_ID")  # Make sure this is set in your .env

# Initialize bot
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Dispatcher and scheduler
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Cache to prevent reposting same headlines
posted_titles = set()

# Scheduled news function
async def send_daily_news():
    news_items = await fetch_anime_news()
    if news_items:
        for news in news_items:
            title = news.get("title", "No title")
            if title in posted_titles:
                continue  # Skip if already posted
            posted_titles.add(title)

            url = news.get("url", "#")
            date = news.get("published_at", "No date")
            image_url = news.get("thumbnail", None)
            text = f"📰 <b>{title}</b>\n\n🗓️ Published: {date}\n🔗 <a href='{url}'>Read More</a>\n\n#AnimeNews #MangaUpdates"

            await bot.send_message(CHAT_ID, text, disable_web_page_preview=True)
            if image_url:
                await bot.send_photo(CHAT_ID, image_url)

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

    # Start the scheduler and register the job
    scheduler.start()
    scheduler.add_job(send_daily_news, IntervalTrigger(hours=24), id="daily_news", max_instances=1)

    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
