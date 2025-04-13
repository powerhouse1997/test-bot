# news.py

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

# Cache file to store sent news
CACHE_FILE = "sent_news_cache.json"

# Function to load cached headlines
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            return json.load(file)
    return {}

# Function to save cached headlines
def save_cache(cache):
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file)

# 🔎 Fetch anime news from AnimeNewsNetwork (only last 24h)
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

        # Extract thumbnail
        image_url = None
        if "media_content" in entry:
            image_url = entry.media_content[0].get("url")
        else:
            desc = entry.get("description", "")
            match = re.search(r'<img[^>]+src="([^"]+)"', desc)
            if match:
                image_url = match.group(1)

        news_items.append({
            "title": entry.title,
            "url": entry.link,
            "published_at": published_time.strftime("%Y-%m-%d %H:%M UTC"),
            "thumbnail": image_url,
            "id": entry.link  # use URL as unique ID
        })

    return news_items

# 🤖 /news command handler
@router.message(Command("news"))
async def cmd_news(message: types.Message, bot: Bot):
    news_items = await fetch_anime_news()

    if not news_items:
        await message.reply("No news available right now.")
        return

    # Load cache
    cache = load_cache()

    for news in news_items:
        news_id = news.get("id")
        if news_id in cache:
            continue  # Already sent

        title = escape(news.get("title", "No title"))
        url = news.get("url", "#")
        date = escape(news.get("published_at", "No date"))
        thumbnail = news.get("thumbnail")

        # Dynamic hashtags and engaging content
        caption = (
            f"📰 <b>{title}</b>\n\n"
            f"<i>📅 <u>Published on:</u></i> <code>{date}</code>\n\n"
            f"<b>🚨 Latest Update:</b>\n\n"
            f"🔗 <a href='{url}'>Read Full Article</a>\n\n"
            f"<i>✨ Stay ahead of the curve with the latest in "
            f"{'anime' if 'anime' in title.lower() else 'manga'} updates!</i>\n\n"  # Detect anime or manga
            f"💬 <b>Share your thoughts below!</b>\n\n"
            f"<b>#{'AnimeNews' if 'anime' in title.lower() else 'MangaNews'} "
            f"#Trending</b>\n\n"  # Dynamic hashtag based on the content
        )

        # Send the message with or without a thumbnail
        if thumbnail:
            await bot.send_photo(message.chat.id, thumbnail, caption=caption, parse_mode="HTML")
        else:
            await bot.send_message(message.chat.id, caption, parse_mode="HTML")

        # Update cache to prevent re-sending the same news
        cache[news_id] = news["published_at"]

    # Save the updated cache
    save_cache(cache)

# Send daily news using the same logic but without the command handler
async def send_daily_news(bot: Bot):
    news_items = await fetch_anime_news()
    cache = load_cache()

    chat_id = os.getenv("YOUR_CHAT_ID")  # Get chat ID from environment variable

    if not chat_id:
        print("⚠️ Please set YOUR_CHAT_ID in .env file.")
        return

    for news in news_items:
        news_id = news.get("id")
        if news_id in cache:
            continue  # Already sent

        caption = f"📰 <b>{escape(news['title'])}</b>\n🗓️ {escape(news['published_at'])}\n🔗 <a href='{news['url']}'>Read Full Article</a>\n\n#AnimeNews #MangaUpdates"

        if news["thumbnail"]:
            await bot.send_photo(chat_id, news["thumbnail"], caption=caption, parse_mode="HTML")
        else:
            await bot.send_message(chat_id, caption, parse_mode="HTML")

        cache[news_id] = news["published_at"]

    save_cache(cache)  # Save updated cache
