from aiogram import types
from aiogram.filters import Command
from jikan_api import search_jikan

def register_top(dp):
    @dp.message(Command("t"))
    async def cmd_top(message: types.Message):
        results = await search_jikan("top/anime")
        if not results:
            await message.reply("No top anime found.")
            return

        for anime in results[:5]:
            caption = (
                f"🏆 <b>{anime['title']}</b>\n"
                f"⭐ Score: {anime.get('score', 'N/A')}\n"
                f"🎬 Episodes: {anime.get('episodes', 'Unknown')}\n"
                f"🔗 <a href='{anime['url']}'>More Info</a>\n\n"
                f"{anime.get('synopsis', '')[:400]}..."
            )
            await message.bot.send_photo(
                message.chat.id,
                anime['images']['jpg']['large_image_url'],
                caption=caption,
                parse_mode="HTML"
            )
