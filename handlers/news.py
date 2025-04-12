from aiogram import types, Router
from aiogram.filters import Command
from html import escape
from news_fetcher import fetch_anime_news  # adjust name if needed

router = Router()

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

        caption = f"📰 <b>{title}</b>\n\n🗓️ <i>{date}</i>\n🔗 <a href='{url}'>Read More</a>\n\n#AnimeNews"

        if thumbnail:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=caption,
                parse_mode="HTML"
            )
        else:
            await message.bot.send_message(
                chat_id=message.chat.id,
                text=caption,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
