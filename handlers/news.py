import feedparser
import re
from aiogram import types, Router
from aiogram.filters import Command
from html import escape

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
