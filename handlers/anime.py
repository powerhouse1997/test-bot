from aiogram import Router, types
from aiogram.filters import Command
from jikan_api import search_jikan

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
    caption = (
        f"🎬 <b>{anime['title']}</b>\n"
        f"⭐ Score: {anime.get('score', 'N/A')}\n"
        f"📺 Episodes: {anime.get('episodes', 'Unknown')}\n"
        f"🔗 <a href='{anime['url']}'>More Info</a>\n\n"
        f"{anime.get('synopsis', '')[:500]}..."
    )
    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=anime['images']['jpg']['large_image_url'],
        caption=caption
    )
