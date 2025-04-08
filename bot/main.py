import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application
from . import handlers, reminders, scheduler, database
from bot.utils import parse_reminder_time
from telegram.ext import ApplicationBuilder
from bot.reminders import check_reminders_loop


async def start_reminders(application):
application.create_task(check_reminders_loop(application.bot))
def main():
    app = ApplicationBuilder().token("YOUR_TOKEN").post_init(start_reminders).build()
    app.run_polling()

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
    async def on_startup(application):
    application.create_task(reminders.reminder_loop(application.bot))
    logging.info("Reminder loop started!")

def main():
    # Get Bot Token from Environment Variable
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN is not set in environment variables!")

    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add Handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_update))
    application.add_handler(MessageHandler(filters.COMMAND, handlers.handle_update))
    application.add_handler(CallbackQueryHandler(handlers.handle_update))

    # Run Reminder Loop AFTER app starts
    application.post_init(on_startup)

    # Start polling
    application.run_polling()

async def on_shutdown():
    print("Bot is shutting down...")

# Entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
