from aiogram import types
from aiogram.filters import Command
from jikan_api import fetch_anime_news
from aiogram import Router

router = Router()

@router.message(Command("news"))
async def cmd_news(message: types.Message):
    # Fetch news items from Jikan API
    news_items = await fetch_anime_news()

    # If fetch_anime_news() returns None or an empty list, handle the no news case
    if not news_items:
        await message.reply("No news available right now.")
        return
    
    # Loop through the news items and send each one
    for news in news_items:
        title = news.get('title', 'No title')
        url = news.get('url', '#')
        date = news.get('published_at', 'No date')
        text = f"📰 <b>{title}</b>\n\n🗓️ Published: {date}\n🔗 <a href='{url}'>Read More</a>\n\n#AnimeNews #MangaUpdates"
        await message.bot.send_message(message.chat.id, text, parse_mode="HTML", disable_web_page_preview=True)

# Register the news command handler
def register_news(dp):
    dp.include_router(router)
