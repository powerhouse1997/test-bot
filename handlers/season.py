from aiogram import types
from aiogram.filters import Command
from jikan_api import fetch_json
from config import JIKAN_API_URL
import asyncio

def register_season(dp):
    @dp.message(Command("s"))
    async def cmd_season(message: types.Message):
        data = await fetch_json(f"{JIKAN_API_URL}/seasons/now")
        if not data or not data.get("data"):
            await message.reply("Couldn't fetch seasonal anime.")
            return
        for anime in data["data"][:5]:
            try:
                caption = (
                    f"📺 <b>{anime['title']}</b>
"
                    f"🎬 Episodes: {anime.get('episodes', 'Unknown')}
"
                    f"⭐ Score: {anime.get('score', 'N/A')}
"
                    f"🔗 <a href='{anime['url']}'>Details</a>"
                )
                await message.bot.send_photo(message.chat.id, anime['images']['jpg']['large_image_url'], caption=caption, parse_mode="HTML")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Error: {e}")
