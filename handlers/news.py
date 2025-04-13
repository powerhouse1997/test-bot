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
async def cmd_news(message: types.Message):
    news_items = await fetch_anime_news()

    if not news_items:
        await message.reply("No news available right now.")
        return

    for news in news_items:
        title = escape(news.get("title", "No title"))
        url = news.get("url", "#")
        date = escape(news.get("published_at", "No date"))
        thumbnail = news.get("thumbnail")

        caption = (
                    f"<b>📰 {title}</b>\n"
                    f"<i>📅 Published on:</i> <code>{date}</code>\n\n"
                    f"🔗 <a href='{url}'>Click here to read the full article</a>\n\n"
                    f"<b>#AnimeNews #MangaUpdates</b>"
)


        if thumbnail:
            await message.bot.send_photo(message.chat.id, photo=thumbnail, caption=caption, parse_mode="HTML")
        else:
            await message.bot.send_message(message.chat.id, caption, parse_mode="HTML")

# 💾 Cache to prevent duplicate posts
CACHE_FILE = "sent_news_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file)

# 🔁 Scheduled news sender
async def send_daily_news(bot: Bot):
    news_items = await fetch_anime_news()
    cache = load_cache()
    chat_id = os.getenv("YOUR_CHAT_ID")  # Put this in your .env

    if not chat_id:
        print("⚠️ Please set YOUR_CHAT_ID in .env file.")
        return

    for news in news_items:
        news_id = news.get("id")
        if news_id in cache:
            continue  # Already sent

        caption = f"📰 <b>{escape(news['title'])}</b>\n🗓️ {escape(news['published_at'])}\n🔗 <a href='{news['url']}'>Read More</a>\n\n#AnimeNews #MangaUpdates"

        if news["thumbnail"]:
            await bot.send_photo(chat_id, news["thumbnail"], caption=caption, parse_mode="HTML")
        else:
            await bot.send_message(chat_id, caption, parse_mode="HTML")

        cache[news_id] = news["published_at"]

    save_cache(cache)
