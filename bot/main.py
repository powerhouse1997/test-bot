import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application
from . import handlers, reminders, scheduler, database
from bot.utils import parse_reminder_time

# Example usage
reminder_str = "in 10 minutes"
reminder_time = parse_reminder_time(reminder_str)

if reminder_time:
    print(f"Reminder set for: {reminder_time}")
else:
    print("Could not parse reminder time.")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN")

bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

app = FastAPI()

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await handlers.handle_update(update, bot)
    return "OK"

@app.on_event("startup")
async def on_startup():
    print("Starting bot...")
    await bot.set_webhook(url=f"{DOMAIN}/")
    reminders.load_reminders()
    application.create_task(reminders.reminder_loop(bot))
    asyncio.create_task(scheduler.daily_summary(bot, database))

@app.on_event("shutdown")
async def on_shutdown():
    print("Bot is shutting down...")

# Entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
