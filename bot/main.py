import asyncio
import logging
import random
import aiohttp
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import feedparser

# Load .env
load_dotenv()

# Your bot token and chat ID
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Logging
logging.basicConfig(level=logging.INFO)

# Global leaderboard
leaderboard = {}

# Anime Quotes
anime_quotes = [
    "“A lesson without pain is meaningless.” – Fullmetal Alchemist: Brotherhood",
    "“Fear is not evil. It tells you what your weakness is.” – Fairy Tail",
    "“The world’s not perfect. But it’s there for us.” – Fullmetal Alchemist",
    "“Hard work is worthless for those that don’t believe in themselves.” – Naruto",
]

async def fetch_anime_news():
    try:
        feed = feedparser.parse('https://www.animenewsnetwork.com/all/rss.xml?ann-edition=us')
        news_items = []
        for entry in feed.entries[:5]:
            news_items.append({
                'title': entry.title,
                'url': entry.link,
                'published_at': entry.published,
            })
        return news_items
    except Exception as e:
        logging.error(f"Error fetching anime news: {e}")
    return []

async def fetch_trending_anime():
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.jikan.moe/v4/top/anime"
            async with session.get(url) as response:
                if response.status == 200:
                    trending = await response.json()
                    return trending.get('data', [])[:5]
    except Exception as e:
        logging.error(f"Error fetching trending anime: {e}")
    return []

async def fetch_countdown_anime():
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.jikan.moe/v4/seasons/upcoming"
            async with session.get(url) as response:
                if response.status == 200:
                    countdown = await response.json()
                    return countdown.get('data', [])[:3]
    except Exception as e:
        logging.error(f"Error fetching countdown anime: {e}")
    return []

async def fetch_random_anime():
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.jikan.moe/v4/random/anime"
            async with session.get(url) as response:
                if response.status == 200:
                    anime = await response.json()
                    return anime.get('data', {})
    except Exception as e:
        logging.error(f"Error fetching random anime: {e}")
    return {}

async def send_latest_news(bot, chat_id):
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

async def send_trending_anime(bot, chat_id):
    trending = await fetch_trending_anime()
    if not trending:
        return
    await update_leaderboard(trending)

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

async def send_daily_quote(bot, chat_id):
    quote = random.choice(anime_quotes)
    await bot.send_message(chat_id, f"✨ <i>{quote}</i> ✨", parse_mode=ParseMode.HTML)

async def send_guess_the_anime(bot, chat_id):
    trending = await fetch_trending_anime()
    if not trending:
        return

    anime = random.choice(trending)
    options = [anime['title']] + [random.choice(trending)['title'] for _ in range(3)]
    random.shuffle(options)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for opt in options:
        markup.add(opt)

    await bot.send_photo(
        chat_id,
        photo=anime['images']['jpg']['large_image_url'],
        caption="🔎 <b>Guess the Anime!</b>",
        reply_markup=markup,
        parse_mode=ParseMode.HTML
    )

async def update_leaderboard(anime_list):
    for anime in anime_list:
        title = anime['title']
        leaderboard[title] = leaderboard.get(title, 0) + 1

async def show_leaderboard(chat_id):
    top = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]
    text = "🏆 <b><u>TOP 5 Trending Anime</u></b> 🏆\n\n"
    for idx, (title, count) in enumerate(top, 1):
        text += f"{idx}. {title} — {count} points\n"
    await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)

async def send_anime_of_the_day(bot, chat_id):
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

# Bot command handlers
@dp.message(Command("news"))
async def cmd_news(message: types.Message):
    await send_latest_news(bot, message.chat.id)

@dp.message(Command("trend"))
async def cmd_trend(message: types.Message):
    await send_trending_anime(bot, message.chat.id)

@dp.message(Command("countdown"))
async def cmd_countdown(message: types.Message):
    await send_anime_countdown(bot, message.chat.id)

@dp.message(Command("quote"))
async def cmd_quote(message: types.Message):
    await send_daily_quote(bot, message.chat.id)

@dp.message(Command("guess"))
async def cmd_guess(message: types.Message):
    await send_guess_the_anime(bot, message.chat.id)

@dp.message(Command("leaderboard"))
async def cmd_leaderboard(message: types.Message):
    await show_leaderboard(message.chat.id)

@dp.message(Command("animeoftheday"))
async def cmd_anime_of_the_day(message: types.Message):
    await send_anime_of_the_day(bot, message.chat.id)

# Start the bot
async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    scheduler.add_job(send_trending_anime, 'interval', hours=6, args=[bot, CHAT_ID])
    scheduler.add_job(send_latest_news, 'interval', hours=4, args=[bot, CHAT_ID])
    scheduler.add_job(send_anime_countdown, 'cron', hour=9, args=[bot, CHAT_ID])
    scheduler.add_job(send_daily_quote, 'cron', hour=10, args=[bot, CHAT_ID])
    scheduler.add_job(send_anime_of_the_day, 'cron', hour=12, args=[bot, CHAT_ID])

    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())