import feedparser
import re
from aiogram import types, Router
from aiogram.filters import Command
from html import escape
import json


router = Router()

async def fetch_anime_news():
    url = "https://www.animenewsnetwork.com/all/rss.xml"
    feed = feedparser.parse(url)

    news_items = []
    for entry in feed.entries[:5]:
        # Try getting thumbnail from media content
        image_url = None
        if "media_content" in entry:
            image_url = entry.media_content[0].get("url")

        news_items.append({
            "title": entry.title,
            "url": entry.link,
            "published_at": entry.published,
            "thumbnail": image_url
        })

    return news_items


@router.message(Command("news"))
async def cmd_news(message: types.Message):
    news_items = await fetch_anime_news()

    if not news_items:
        await message.reply("No news available right now.")
        return

    for news in news_items:
        title = escape(news.get('title', 'No title'))
        url = news.get('url', '#')
        date = escape(news.get('published_at', 'No date'))
        thumbnail = news.get('thumbnail')

        caption = f"📰 <b>{title}</b>\n🗓️ {date}\n🔗 <a href='{url}'>Read More</a>\n\n#AnimeNews #MangaUpdates"

        if thumbnail:
            await message.bot.send_photo(message.chat.id, photo=thumbnail, caption=caption, parse_mode="HTML")
        else:
            await message.bot.send_message(message.chat.id, caption, parse_mode="HTML")

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

# Function to send daily news with cache check
async def send_daily_news():
    news_items = await fetch_anime_news()
    cache = load_cache()  # Load cached headlines

    if news_items:
        for news in news_items:
            title = news.get('title', 'No title')
            url = news.get('url', '#')
            date = news.get('published_at', 'No date')
            image_url = news.get('image_url', None)
            news_id = news.get('mal_id')  # Assuming mal_id is unique

            # Skip if already sent
            if news_id in cache:
                continue

            text = f"📰 <b>{title}</b>\n\n🗓️ Published: {date}\n🔗 <a href='{url}'>Read More</a>\n\n#AnimeNews #MangaUpdates"
            chat_id = os.getenv("YOUR_CHAT_ID")  # Your chat ID here
            await bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True)
            if image_url:
                await bot.send_photo(chat_id, image_url)

            # Add to cache
            cache[news_id] = title

        # Save updated cache
        save_cache(cache)
