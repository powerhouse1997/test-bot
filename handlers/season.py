from aiogram import types
from aiogram.filters import Command
from jikan_api import fetch_season_now
from aiogram import Router

router = Router()

def register_season(dp):
    @dp.message(Command("s"))
    async def cmd_season(message: types.Message):
        results = await fetch_season_now()
        if not results:
            await message.reply("No seasonal anime found.")
            return

        for anime in results[:5]:
            caption = (
                f"📺 <b>{anime['title']}</b>\n"
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
