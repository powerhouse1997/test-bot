from aiogram import types
from aiogram.filters import Command
from jikan_api import fetch_anime_news

def register_news(dp):
    @dp.message(Command("news"))
    async def cmd_news(message: types.Message):
        news_items = await fetch_anime_news()
        if not news_items:
            await message.reply("No news available right now.")
            return
        for news in news_items:
            title = news.get('title', 'No title')
            url = news.get('url', '#')
            date = news.get('published_at', 'No date')
            text = f"📰 <b>{title}</b>\n\n🗓️ Published: {date}\n🔗 <a href='{url}'>Read More</a>\n\n#AnimeNews #MangaUpdates"
            await message.bot.send_message(message.chat.id, text, parse_mode="HTML", disable_web_page_preview=True)
