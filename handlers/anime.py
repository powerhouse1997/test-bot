from aiogram import types
from aiogram.filters import Command
from jikan_api import search_jikan

def register_anime(dp):
    @dp.message(Command("a"))
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
            f"📅 Aired: {anime.get('aired', 'Unknown')}\n"
            f"🔗 <a href='{anime['url']}'>More Info</a>\n\n"
            f"{anime.get('synopsis', '')[:500]}..."
        )
        await message.bot.send_photo(message.chat.id, anime['image_url'], caption=caption, parse_mode="HTML")
