from aiogram import Router, types
from aiogram.filters import Command
from jikan_api import fetch_season_now  # This should work now
from html import escape

router = Router()

@router.message(Command("season"))
async def cmd_season(message: types.Message):
    data = await fetch_season_now()
    if not data:
        await message.reply("❌ Failed to fetch current season's anime.")
        return
    
    caption = ""
    for anime in data:
        title = escape(anime.get("title", "Unknown"))
        episodes = anime.get("episodes", "Unknown")
        url = anime.get("url", "#")
        synopsis = escape(anime.get("synopsis", "No synopsis available."))[:200]

        caption += f"🎬 <b>{title}</b>\n"
        caption += f"📺 Episodes: {episodes}\n"
        caption += f"🔗 <a href='{url}'>More Info</a>\n\n"
        caption += f"{synopsis}...\n\n"

    await message.reply(caption, parse_mode="HTML")
