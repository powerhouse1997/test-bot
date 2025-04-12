from aiogram import Router, types
from aiogram.filters import Command
from jikan_api import search_jikan
import html

router = Router()

@router.message(Command("a"))
async def cmd_anime(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Usage: /a <anime title>")
        return

    results = await search_jikan("anime", args[1])
    if not results:
        await message.reply("No anime found.")
        return

    anime = results[0]

    title = html.escape(anime['title'])
    synopsis = html.escape(anime.get('synopsis', ''))[:500]
    score = anime.get('score', 'N/A')
    episodes = anime.get('episodes', 'Unknown')
    url = html.escape(anime['url'])

    caption = (
        f"🎬 <b>{title}</b>\n"
        f"⭐ Score: {score}\n"
        f"📺 Episodes: {episodes}\n"
        f"🔗 <a href='{url}'>More Info</a>\n\n"
        f"{synopsis}..."
    )

    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=anime['images']['jpg']['large_image_url'],
        caption=caption,
        parse_mode="HTML"
    )
