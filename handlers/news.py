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

# 🔤 Keywords to filter for anime/manga-only news
WHITELIST_KEYWORDS = [
    "anime", "manga", "japan", "japanese", "otaku", "crunchyroll",
    "myanimelist", "viz", "shonen", "funimation", "anime film", "anime series"
]

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file)

def is_relevant_news(title: str, summary: str) -> bool:
    combined = f"{title.lower()} {summary.lower()}"
    return any(keyword in combined for keyword in WHITELIST_KEYWORDS)

async def fetch_anime_news():
    url = "https://www.animenewsnetwork.com/all/rss.xml"
    feed = feedparser.parse(url)

    now = datetime.utcnow()
    cutoff = now - timedelta(hours=24)

    news_items = []
    for entry in feed.entries:
        title = entry.title
        summary = entry.get("summary", "")
        if not is_relevant_news(title, summary):
            continue

        published_parsed = entry.get("published_parsed")
        if not published_parsed:
            continue

        published_time = datetime.fromtimestamp(time.mktime(published_parsed))
        if published_time < cutoff:
            continue

        image_url = None
        if "media_content" in entry:
            image_url = entry.media_content[0].get("url")
        else:
            match = re.search(r'<img[^>]+src="([^"]+)"', entry.get("description", ""))
            if match:
                image_url = match.group(1)

        news_items.append({
            "title": title,
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
        await message.reply("No relevant anime/manga news found.")
        return

    cache = load_cache()

    for news in news_items:
        news_id = news["id"]
        if news_id in cache:
            continue

        title = escape(news["title"])
        url = news["url"]
        date = escape(news["published_at"])
        thumbnail = news.get("thumbnail")
        tag = "#AnimeNews" if "anime" in title.lower() else "#MangaNews"

        caption = (
            f"📰 <b>{title}</b>\n\n"
            f"<i>📅 <u>Published on:</u></i> <code>{date}</code>\n\n"
            f"<b>🔗 <a href='{url}'>Read Full Article</a></b>\n\n"
            f"💬 What are your thoughts?\n\n"
            f"{tag} #Trending"
        )

        if thumbnail:
            await bot.send_photo(message.chat.id, photo=thumbnail, caption=caption, parse_mode="HTML")
        else:
            await bot.send_message(message.chat.id, text=caption, parse_mode="HTML")

        cache[news_id] = date

    save_cache(cache)

# ✅ Scheduled daily news
async def send_daily_news(bot: Bot):
    news_items = await fetch_anime_news()
    cache = load_cache()
    chat_id = os.getenv("YOUR_CHAT_ID")

    if not chat_id:
        print("⚠️ Please set YOUR_CHAT_ID in your environment.")
        return

    for news in news_items:
        news_id = news["id"]
        if news_id in cache:
            continue

        title = escape(news["title"])
        url = news["url"]
        date = escape(news["published_at"])
        thumbnail = news.get("thumbnail")
        tag = "#AnimeNews" if "anime" in title.lower() else "#MangaNews"

        caption = (
            f"📰 <b>{title}</b>\n\n"
            f"<i>📅 <u>Published on:</u></i> <code>{date}</code>\n\n"
            f"<b>🔗 <a href='{url}'>Read Full Article</a></b>\n\n"
            f"💬 What are your thoughts?\n\n"
            f"{tag} #Trending"
        )

        if thumbnail:
            await bot.send_photo(chat_id, photo=thumbnail, caption=caption, parse_mode="HTML")
        else:
            await bot.send_message(chat_id, text=caption, parse_mode="HTML")

        cache[news_id] = date

    save_cache(cache)
