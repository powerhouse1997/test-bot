from aiogram import types
from aiogram.filters import Command
from jikan_api import fetch_json
from config import JIKAN_API_URL
import asyncio

def register_top(dp):
    @dp.message(Command("t"))
    async def cmd_top(message: types.Message):
        args = message.text.split(maxsplit=1)
        category = args[1] if len(args) > 1 and args[1] in ["manga", "anime"] else "anime"
        data = await fetch_json(f"{JIKAN_API_URL}/top/{category}")
        if not data or not data.get("data"):
            await message.reply(f"No top {category} found.")
            return
        for entry in data["data"][:5]:
            try:
                caption = (
                    f"🏆 <b>{entry['title']}</b>
"
                    f"⭐ Score: {entry.get('score', 'N/A')}
"
                    f"📊 Rank: {entry.get('rank', 'N/A')}
"
                    f"🔗 <a href='{entry['url']}'>More Info</a>"
                )
                await message.bot.send_photo(message.chat.id, entry['images']['jpg']['large_image_url'], caption=caption, parse_mode="HTML")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Error: {e}")
