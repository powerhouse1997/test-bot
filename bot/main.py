import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application
from . import reminders, handlers

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DOMAIN = os.getenv("DOMAIN")

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

@app.route("/", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)   # 🔥 No await here
    update = Update.de_json(data, bot)
    await handlers.handle_update(update, bot)
    return "OK"

async def start():
    await bot.set_webhook(url=f"{DOMAIN}/")
    reminders.load_reminders()             # ✅ No await here
    asyncio.create_task(reminders.reminder_loop(bot))
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

if __name__ == "__main__":
    asyncio.run(start())
