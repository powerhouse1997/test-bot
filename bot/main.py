import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot import handlers, reminders
from bot.utils import parse_reminder_time
from bot.reminders import reminder_loop
from bot.handlers import search_manga

# Load environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN")

if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN is not set in environment variables!")

# Initialize FastAPI app
app = FastAPI()

# Initialize Telegram Bot
bot = Bot(token=BOT_TOKEN)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Example parse reminder
reminder_str = "in 10 minutes"
reminder_time = parse_reminder_time(reminder_str)
if reminder_time:
    print(f"Reminder set for: {reminder_time}")
else:
    print("Could not parse reminder time.")

# ✅ Register your handlers
application.add_handler(CommandHandler("manga", search_manga))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_update))
application.add_handler(MessageHandler(filters.COMMAND, handlers.handle_update))
application.add_handler(CallbackQueryHandler(handlers.handle_update))

# ✅ Webhook endpoint
@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}

# ✅ Startup event
@app.on_event("startup")
async def on_startup():
    logging.info("Starting bot and setting webhook...")
    webhook_url = f"{DOMAIN}/"
    await bot.set_webhook(webhook_url)
    await application.initialize()
    await application.start()
    application.create_task(reminder_loop(bot))
    logging.info("Reminder loop started!")

# ✅ Shutdown event
@app.on_event("shutdown")
async def on_shutdown():
    logging.info("Bot is shutting down...")

# Entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
