import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.utils.markdown import html_decoration
from dotenv import load_dotenv
from handlers.anime import register_anime
from handlers.manga import register_manga
from handlers.character import register_character
from handlers.season import register_season
from handlers.top import register_top
from handlers.news import register_news

# Load .env
load_dotenv()

# Initialize bot and dispatcher
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Register command handlers
register_anime(dp)
register_manga(dp)
register_character(dp)
register_season(dp)
register_top(dp)
register_news(dp)

# Main entry point for the bot
async def on_start():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(on_start())
