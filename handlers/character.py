from aiogram import types
from aiogram.filters import Command
from jikan_api import search_jikan

def register_character(dp):
    @dp.message(Command("c"))
    async def cmd_character(message: types.Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply("Usage: /c <character name>")
            return
        results = await search_jikan("characters", args[1])
        if not results:
            await message.reply("No character found.")
            return
        char = results[0]
        caption = (
            f"👤 <b>{char['name']}</b>\n"
            f"⭐ Favorites: {char.get('favorites', 'N/A')}\n"
            f"🔗 <a href='{char['url']}'>More Info</a>\n\n"
            f"{char.get('about', '')[:500]}..."
        )
        await message.bot.send_photo(
            message.chat.id,
            char['images']['jpg']['image_url'],
            caption=caption,
            parse_mode="HTML"
        )
