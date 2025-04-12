import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers.anime import register_anime
from handlers.manga import register_manga
from handlers.character import register_character
from handlers.season import register_season
from handlers.top import register_top
from handlers.news import register_news

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logging.error("TELEGRAM_BOT_TOKEN is not set in environment variables!")
    exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Register command handlers
register_anime(dp)
register_manga(dp)
register_character(dp)
register_season(dp)
register_top(dp)
register_news(dp)

# Main entry point for the bot
async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
