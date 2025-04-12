import asyncio
import logging
import random
import aiohttp
import os
import feedparser
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Your bot token and chat ID
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
JIKAN_API_URL = os.getenv("JIKAN_API_URL", "https://api.jikan.moe/v4")

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Logging
logging.basicConfig(level=logging.INFO)

# Anime Quotes
anime_quotes = [
    "“A lesson without pain is meaningless.” – Fullmetal Alchemist: Brotherhood",
    "“Fear is not evil. It tells you what your weakness is.” – Fairy Tail",
    "“The world’s not perfect. But it’s there for us.” – Fullmetal Alchemist",
    "“Hard work is worthless for those that don’t believe in themselves.” – Naruto",
]

# Jikan API fetching functions
async def fetch_json(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logging.error(f"Failed to fetch {url}: Status {response.status}")
    except Exception as e:
        logging.error(f"Exception while fetching {url}: {e}")
    return None

async def fetch_trending_anime():
    data = await fetch_json(f"{JIKAN_API_URL}/top/anime")
    if data:
        return data.get('data', [])[:5]
    return []

async def fetch_countdown_anime():
    data = await fetch_json(f"{JIKAN_API_URL}/seasons/upcoming")
    if data:
        return data.get('data', [])[:5]
    return []

async def fetch_random_anime():
    data = await fetch_json(f"{JIKAN_API_URL}/random/anime")
    if data:
        return data.get('data')
    return None

# Anime News fetching from RSS
async def fetch_anime_news():
    try:
        feed = feedparser.parse('https://www.animenewsnetwork.com/all/rss.xml?ann-edition=us')
        news_items = []
        for entry in feed.entries[:5]:  # take 5 latest news
            news_items.append({
                'title': entry.title,
                'url': entry.link,
                'published_at': entry.published,
            })
        return news_items
    except Exception as e:
        logging.error(f"Error fetching anime news: {e}")
    return []

# Scheduler tasks to send anime updates
async def send_trending_anime(bot, chat_id):
    trending = await fetch_trending_anime()
    if not trending:
        return
    for anime in trending:
        try:
            title = anime['title']
            image = anime['images']['jpg']['large_image_url']
            rating = anime.get('score', 'N/A')
            episodes = anime.get('episodes', 'Unknown')
            status = anime.get('status', 'Unknown')
            genres = ', '.join([genre['name'] for genre in anime.get('genres', [])])

            caption = (
                f"✨ <b><u>{title}</u></b>\n\n"
                f"⭐ <b>Rating:</b> {rating}\n"
                f"🎬 <b>Episodes:</b> {episodes}\n"
                f"📺 <b>Status:</b> {status}\n"
                f"🎭 <b>Genres:</b> {genres}\n\n"
                f"#TrendingAnime #HotNow"
            )
            await bot.send_photo(chat_id, photo=image, caption=caption, parse_mode=ParseMode.HTML)
            await asyncio.sleep(2)
        except Exception as e:
            logging.error(f"Error sending trending anime: {e}")

async def send_anime_countdown(bot, chat_id):
    countdowns = await fetch_countdown_anime()
    for anime in countdowns:
        try:
            title = anime['title']
            start_date = anime.get('aired', {}).get('from', 'Unknown')
            url = anime.get('url')
            text = (
                f"⏳ <b><u>Countdown to {title}</u></b>\n\n"
                f"📅 <b>Start Date:</b> {start_date}\n"
                f"🔗 <a href='{url}'>Details</a>\n\n"
                f"#UpcomingAnime #AnimeHype"
            )
            await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)
            await asyncio.sleep(2)
        except Exception as e:
            logging.error(f"Error sending countdown: {e}")

async def send_random_anime(bot, chat_id):
    anime = await fetch_random_anime()
    if not anime:
        return

    try:
        title = anime['title']
        image = anime['images']['jpg']['large_image_url']
        rating = anime.get('score', 'N/A')
        episodes = anime.get('episodes', 'Unknown')
        status = anime.get('status', 'Unknown')
        genres = ', '.join([genre['name'] for genre in anime.get('genres', [])])
        url = anime.get('url')

        caption = (
            f"🌟 <b><u>Anime of the Day: {title}</u></b> 🌟\n\n"
            f"⭐ <b>Rating:</b> {rating}\n"
            f"🎬 <b>Episodes:</b> {episodes}\n"
            f"📺 <b>Status:</b> {status}\n"
            f"🎭 <b>Genres:</b> {genres}\n"
            f"🔗 <a href='{url}'>More Info</a>\n\n"
            f"#AnimeOfTheDay #AnimeLover"
        )
        await bot.send_photo(chat_id, photo=image, caption=caption, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Error sending Anime of the Day: {e}")

async def send_anime_news(bot, chat_id):
    news_items = await fetch_anime_news()
    for news in news_items:
        try:
            title = news['title']
            url = news['url']
            date = news['published_at'][:10]
            text = f"📰 <b><u>{title}</u></b>\n\n🗓️ Published: {date}\n🔗 <a href='{url}'>Read More</a>\n\n#AnimeNews #MangaUpdates"
            await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            await asyncio.sleep(2)
        except Exception as e:
            logging.error(f"Error sending news: {e}")

# Bot command handlers
@dp.message(Command("trend"))
async def cmd_trend(message: types.Message):
    await send_trending_anime(bot, message.chat.id)

@dp.message(Command("countdown"))
async def cmd_countdown(message: types.Message):
    await send_anime_countdown(bot, message.chat.id)

@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    await send_random_anime(bot, message.chat.id)

@dp.message(Command("news"))
async def cmd_news(message: types.Message):
    await send_anime_news(bot, message.chat.id)

# Start the bot
async def main():
    # Ensure webhook is deleted before starting polling
    await bot.delete_webhook(drop_pending_updates=True)

    # Schedule regular tasks (e.g. sending updates every 6 hours)
    scheduler.add_job(send_trending_anime, 'interval', hours=6, args=[bot, CHAT_ID])
    scheduler.add_job(send_anime_countdown, 'cron', hour=9, args=[bot, CHAT_ID])
    scheduler.add_job(send_random_anime, 'cron', hour=12, args=[bot, CHAT_ID])
    scheduler.add_job(send_anime_news, 'interval', hours=4, args=[bot, CHAT_ID])

    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())