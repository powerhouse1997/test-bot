# news_ann.py
import feedparser
import html
import json
import os
from datetime import datetime
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

NEWS_FEED_URL = "https://www.animenewsnetwork.com/all/rss.xml"
CACHE_FILE = "sent_news_cache.json"
NEWS_KEYWORDS = ["anime", "manga", "japan", "otaku", "light novel"]

def load_sent_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(cache), f)

async def fetch_ann_news():
    return feedparser.parse(NEWS_FEED_URL)

def filter_news(entries, sent_cache):
    new_items = []
    for entry in entries:
        entry_id = entry.get("id") or entry.get("link")
        title = entry.get("title", "").lower()
        summary = entry.get("summary", "").lower()

        if entry_id in sent_cache:
            continue

        if any(keyword in title or keyword in summary for keyword in NEWS_KEYWORDS):
            new_items.append(entry)
            sent_cache.add(entry_id)

    return new_items

async def send_news(bot: Bot, chat_id: int):
    sent_cache = load_sent_cache()
    feed = await fetch_ann_news()
    new_items = filter_news(feed.entries, sent_cache)

    for item in new_items:
        title = html.escape(item.get("title", "No Title"))
        link = item.get("link", "")
        summary = html.escape(item.get("summary", "")[:500])

        # Try to fetch the image URL
        img_url = None
        if "media_thumbnail" in item:
            img_url = item["media_thumbnail"][0]["url"]

        message = f"<b>{title}</b>\n\n{summary}\n\n<a href='{link}'>Read more</a>"

        if img_url:
            # Send message with image preview
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML", disable_web_page_preview=False)
            await bot.send_photo(chat_id=chat_id, photo=img_url)
        else:
            # Send message without image
            await bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML", disable_web_page_preview=False)

    if new_items:
        save_sent_cache(sent_cache)

def schedule_ann_news(scheduler: AsyncIOScheduler, bot: Bot, chat_id: int):
    scheduler.add_job(send_news, "interval", minutes=30, args=[bot, chat_id], next_run_time=datetime.now())
