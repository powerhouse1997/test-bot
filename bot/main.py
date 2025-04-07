# bot/main.py
import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.request import AiohttpRequest
from . import reminders, handlers

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN")

app = FastAPI()

request_client = AiohttpRequest()
bot = Bot(token=BOT_TOKEN, request=request_client)

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
