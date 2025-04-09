import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from bot import handlers, reminders
from bot.utils import parse_reminder_time
from bot.reminders import reminder_loop
from bot.handlers import search_manga
from bot.models import init_db
from bot.handlers import add_power, remove_power
from bot.power_manager import load_power_users

# Inside your `on_startup` function
application.add_handler(CommandHandler("addpower", add_power))
application.add_handler(CommandHandler("removepower", remove_power))

# Load environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN")

if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN is not set in environment variables!")

# Initialize FastAPI app
app = FastAPI()

# Initialize Telegram Application
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
    update = Update.de_json(data, application.bot)  # use application.bot, not bot
    await application.process_update(update)
    return {"ok": True}

# ✅ Startup event
@app.on_event("startup")
async def on_startup():
    logging.info("🚀 Starting bot...")
    init_db()


    await application.initialize()
    load_power_users()

    await application.start()
    await application.initialize()
    await application.start()

    webhook_url = f"{DOMAIN}/"
    await application.bot.set_webhook(webhook_url)

    # Reminder loop
    application.create_task(reminder_loop(application.bot))
    
    logging.info("✅ Bot started and reminder loop running!")

# ✅ Shutdown event
@app.on_event("shutdown")
async def on_shutdown():
    logging.info("Bot is shutting down...")

# ✅ Entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
