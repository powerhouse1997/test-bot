from aiogram import types
from aiogram.filters import Command
from jikan_api import search_jikan

router = Router()

def register_manga(dp):
    @dp.message(Command("m"))
    async def cmd_manga(message: types.Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply("Usage: /m <manga title>")
            return
        results = await search_jikan("manga", args[1])
        if not results:
            await message.reply("No manga found.")
            return
        manga = results[0]
        caption = f"""📚 <b>{manga['title']}</b>
⭐ Score: {manga.get('score', 'N/A')}
📖 Chapters: {manga.get('chapters', 'Unknown')}
🔗 <a href='{manga['url']}'>More Info</a>

{manga.get('synopsis', '')[:500]}..."""
        await message.bot.send_photo(
            message.chat.id,
            manga['images']['jpg']['large_image_url'],
            caption=caption,
            parse_mode="HTML"
        )
