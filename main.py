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
from news_fetcher import fetch_anime_news  # Assuming this fetches the news

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize bot
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Initialize dispatcher with the bot instance
dp = Dispatcher()

# Scheduler setup
scheduler = AsyncIOScheduler()

# Function to send daily news
async def send_daily_news():
    news_items = await fetch_anime_news()
    if news_items:
        for news in news_items:
            title = news.get('title', 'No title')
            url = news.get('url', '#')
            date = news.get('published_at', 'No date')
            image_url = news.get('image_url', None)
            text = f"📰 <b>{title}</b>\n\n🗓️ Published: {date}\n🔗 <a href='{url}'>Read More</a>\n\n#AnimeNews #MangaUpdates"
            chat_id = os.getenv("YOUR_CHAT_ID")  # Your chat ID here
            await bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True)
            if image_url:
                await bot.send_photo(chat_id, image_url)

# Register all routers
dp.include_router(anime_router)
dp.include_router(manga_router)
dp.include_router(character_router)
dp.include_router(season_router)
dp.include_router(top_router)
dp.include_router(news_router)

# Start scheduler for daily news
scheduler.add_job(send_daily_news, IntervalTrigger(hours=24), id='daily_news', max_instances=1)

# Start the scheduler
scheduler.start()

# Entry point
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
