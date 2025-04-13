import os
import json
import re
import feedparser
import time
from datetime import datetime, timedelta
from aiogram import types, Router, Bot
from aiogram.filters import Command
from html import escape

router = Router()

CACHE_FILE = "sent_news_cache.json"

# ✅ Only include news with these keywords
WHITELIST_KEYWORDS = ["anime", "manga", "anime series", "anime film", "anime movie", "anime adaptation"]

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file)

async def fetch_anime_news():
    url = "https://www.animenewsnetwork.com/all/rss.xml"
    feed = feedparser.parse(url)

    now = datetime.utcnow()
    twenty_four_hours_ago = now - timedelta(hours=24)

    news_items = []
    for entry in feed.entries:
        published_parsed = entry.get("published_parsed")
        if not published_parsed:
            continue

        published_time = datetime.fromtimestamp(time.mktime(published_parsed))
        if published_time < twenty_four_hours_ago:
            continue

        title_lower = entry.title.lower()

        # ✅ Filter by keywords
        if not any(keyword in title_lower for keyword in WHITELIST_KEYWORDS):
            continue

        # Extract thumbnail
        image_url = None
        if "media_content" in entry:
            image_url = entry.media_content[0].get("url")
        else:
            desc = entry.get("description", "")
            match = re.search(r'<img[^>]+src="([^"]+)"', desc)
            if match:
                image_url = match.group(1)

        if not image_url:
            continue  # ✅ Skip if no image

        news_items.append({
            "title": entry.title,
            "url": entry.link,
            "published_at": published_time.strftime("%Y-%m-%d %H:%M UTC"),
            "thumbnail": image_url,
            "id": entry.link
        })

    return news_items

@router.message(Command("news"))
async def cmd_news(message: types.Message, bot: Bot):
    news_items = await fetch_anime_news()

    if not news_items:
        await message.reply("No news available right now.")
        return

    cache = load_cache()

    for news in news_items:
        news_id = news.get("id")
        if news_id in cache:
            continue

        title = escape(news.get("title", "No title"))
        url = news.get("url", "#")
        date = escape(news.get("published_at", "No date"))
        thumbnail = news.get("thumbnail")

        is_manga = "manga" in title.lower()
        hashtags = "#MangaNews" if is_manga else "#AnimeNews"

        caption = (
            f"📰 <b>{title}</b>\n\n"
            f"<i>📅 <u>Published on:</u></i> <code>{date}</code>\n\n"
            f"🔗 <a href='{url}'>Read Full Article</a>\n\n"
            f"<i>✨ Stay ahead with the latest in {'manga' if is_manga else 'anime'} updates!</i>\n\n"
            f"<b>{hashtags} #Trending</b>"
        )

        await bot.send_photo(message.chat.id, thumbnail, caption=caption, parse_mode="HTML")
        cache[news_id] = news["published_at"]

    save_cache(cache)

async def send_daily_news(bot: Bot):
    news_items = await fetch_anime_news()
    cache = load_cache()

    chat_id = os.getenv("YOUR_CHAT_ID")
    if not chat_id:
        print("⚠️ Please set YOUR_CHAT_ID in .env file.")
        return

    for news in news_items:
        news_id = news.get("id")
        if news_id in cache:
            continue

        title = escape(news.get("title", "No title"))
        url = news.get("url", "#")
        date = escape(news.get("published_at", "No date"))
        thumbnail = news.get("thumbnail")

        is_manga = "manga" in title.lower()
        hashtags = "#MangaNews" if is_manga else "#AnimeNews"

        caption = (
            f"📰 <b>{title}</b>\n\n"
            f"<i>📅 <u>Published on:</u></i> <code>{date}</code>\n\n"
            f"🔗 <a href='{url}'>Read Full Article</a>\n\n"
            f"<i>✨ Stay ahead with the latest in {'manga' if is_manga else 'anime'} updates!</i>\n\n"
            f"<b>{hashtags} #Trending</b>"
        )

        await bot.send_photo(chat_id, thumbnail, caption=caption, parse_mode="HTML")
        cache[news_id] = news["published_at"]

    save_cache(cache)
