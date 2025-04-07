import os
import asyncio
import aiohttp
from fastapi import FastAPI, Request
from telegram import Update, Bot
from . import reminders, handlers

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN")

app = FastAPI()

bot: Bot = None
session: aiohttp.ClientSession = None

@app.on_event("startup")
async def on_startup():
    global bot, session
    session = aiohttp.ClientSession()
    bot = Bot(token=BOT_TOKEN, session=session)

    await bot.set_webhook(url=f"{DOMAIN}/")
    reminders.load_reminders()
    asyncio.create_task(reminders.reminder_loop(bot))

@app.on_event("shutdown")
async def on_shutdown():
    global session
    if session:
        await session.close()

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await handlers.handle_update(update, bot)
    return {"ok": True}
