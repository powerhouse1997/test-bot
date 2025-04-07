import os
import asyncio
import aiohttp
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from telegram import Update, Bot
from . import reminders, handlers

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN")

bot: Bot = None
session: aiohttp.ClientSession = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot, session
    # Startup
    session = aiohttp.ClientSession()
    bot = Bot(token=BOT_TOKEN, session=session)

    await bot.set_webhook(url=f"{DOMAIN}/")
    reminders.load_reminders()
    asyncio.create_task(reminders.reminder_loop(bot))

    yield  # App runs here

    # Shutdown
    await session.close()

app = FastAPI(lifespan=lifespan)

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await handlers.handle_update(update, bot)
    return {"ok": True}
