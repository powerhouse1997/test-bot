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
from bot import handlers, moderation, welcome, stats, scheduler
from bot.utils import parse_reminder_time
from bot.power_manager import load_power_users
from bot.scheduler import reminder_loop
from bot.handlers import features

# Load environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN")

if not BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN is not set in environment variables!")

# Initialize FastAPI app
app = FastAPI()
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Setup logging
logging.basicConfig(level=logging.INFO)

# ✅ Register your handlers
application.add_handler(CommandHandler("power", handlers.power_command))
application.add_handler(CommandHandler("summary", handlers.daily_summary))
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome.welcome_new_member))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.chat_handler))
application.add_handler(MessageHandler(filters.COMMAND, moderation.command_handler))
application.add_handler(CallbackQueryHandler(handlers.button_callback))
application.add_handler(CommandHandler("features", features)) 


@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    logging.info("🚀 Starting bot...")
    load_power_users()
    await application.initialize()
    await application.start()
    webhook_url = f"{DOMAIN}/"
    await application.bot.set_webhook(webhook_url)
    application.create_task(reminder_loop(application.bot))
    logging.info("✅ Bot started and reminder loop running!")

@app.on_event("shutdown")
async def on_shutdown():
    logging.info("Bot is shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
# Final main.py code will go here
