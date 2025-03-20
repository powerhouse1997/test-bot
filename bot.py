from flask import Flask, request
from telegram import Update
import bot
from telegram.ext import Application, CommandHandler, ContextTypes
import os

app = Flask(__name__)

# Bot Token
TOKEN = os.getenv("BOT_TOKEN", "6438781804:AAGvcF5pp2gg2Svr5f0kpxvG9ZMoiG1WACc")
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I am your bot. 😊")

# Add command handlers
application.add_handler(CommandHandler("start", start))

# ✅ Webhook Route (This should exist)
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    application.process_update(update)
    return "OK", 200

# ✅ Health Check Route (To check if bot is running)
@app.route('/', methods=['GET'])
def home():
    return "Bot is running!", 200

if __name__ == "__main__":
    print("Starting bot...")
    app.run(host="0.0.0.0", port=8000)
    
