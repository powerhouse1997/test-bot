import asyncio
from aiogram import Bot, Dispatcher
from handlers.anime import register_anime
from handlers.manga import register_manga
from handlers.character import register_character
from handlers.season import register_season
from handlers.top import register_top
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Register all handlers
register_anime(dp)
register_manga(dp)
register_character(dp)
register_season(dp)
register_top(dp)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
