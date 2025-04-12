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
        # Try to find image in description HTML
        img_match = re.search(r'<img[^>]+src="([^"]+)"', entry.description)
        image_url = img_match.group(1) if img_match else None
        
        print("🖼️ Image URL:", image_url)  # Debug log

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

        text = f"📰 <b>{title}</b>\n🗓️ Published: {date}\n🔗 <a href='{url}'>Read More</a>\n\n#AnimeNews #MangaUpdates"

        if thumbnail:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=text,
                parse_mode="HTML"
            )
        else:
            await message.bot.send_message(
                chat_id=message.chat.id,
                text=text,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
