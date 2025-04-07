import os
import asyncio
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler
from . import reminders, handlers

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN")

async def start_bot():
    application = Application.builder().token(BOT_TOKEN).build()

    # Register your handlers here
    application.add_handler(handlers.get_handler())  # assuming you have a `get_handler` function

    # Load reminders
    reminders.load_reminders()
    
    # Start reminder loop
    asyncio.create_task(reminders.reminder_loop(application.bot))

    # Start the webhook server
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        webhook_url=f"{DOMAIN}/",
    )

if __name__ == "__main__":
    asyncio.run(start_bot())

