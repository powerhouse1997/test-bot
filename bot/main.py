# bot/main.py
import os
import asyncio
import aiohttp
from fastapi import FastAPI, Request
from telegram import Update, Bot
from . import reminders, handlers

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN")

app = FastAPI()

session = aiohttp.ClientSession()
bot = Bot(token=BOT_TOKEN, session=session)

@app.post("/")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await handlers.handle_update(update, bot)
    return {"status": "ok"}

async def start_bot():
    await bot.set_webhook(url=f"{DOMAIN}/")
    reminders.load_reminders()
    asyncio.create_task(reminders.reminder_loop(bot))

@app.on_event("startup")
async def startup_event():
    await start_bot()

@app.on_event("shutdown")
async def shutdown_event():
    await session.close()
