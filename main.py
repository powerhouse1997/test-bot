import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties


# Import routers from handlers
from handlers.anime import router as anime_router
from handlers.manga import router as manga_router
from handlers.character import router as character_router
from handlers.season import router as season_router
from handlers.top import router as top_router
from handlers.news import router as news_router

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def main():
    logging.basicConfig(level=logging.INFO)

    # Initialize bot and dispatcher
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

    # Include routers
dp.include_router(anime_router)
dp.include_router(manga_router)
dp.include_router(character_router)
dp.include_router(season_router)
dp.include_router(top_router)
dp.include_router(news_router)

    # Start polling
await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
