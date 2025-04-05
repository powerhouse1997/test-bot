import os
import asyncio
import datetime
import requests
import dateparser
from flask import Flask, request
from googletrans import Translator
from anthropic import AsyncAnthropic
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

if not BOT_TOKEN or not CLAUDE_API_KEY or not WEATHER_API_KEY:
    raise ValueError("Missing API keys.")

# Initialize services
anthropic = AsyncAnthropic(api_key=CLAUDE_API_KEY)
translator = Translator()
app = Flask(__name__)
notes = {}
reminders = {}

# Helper functions
async def get_ai_response_claude(user_message: str) -> str:
    try:
        message = await anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f"Claude API Error: {e}")
        return "Claude AI error."

async def get_weather(city: str) -> str:
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") != "404":
            main = response["main"]
            description = response["weather"][0]["description"]
            return f"Weather in {city}: {description}, Temp: {main['temp']}°C, Humidity: {main['humidity']}%"
        else:
            return "City not found."
    except Exception as e:
        print(f"Weather API Error: {e}")
        return "Weather service error."

async def translate_text(text: str, target_language: str) -> str:
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        print(f"Translation Error: {e}")
        return "Translation error."

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your assistant bot 🤖. Type /help to see commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/notes - Show your notes\n"
        "Reply with 'note this' to a message to save it\n"
        "/weather <city> - Get weather info\n"
        "/translate <lang_code> <text> - Translate text\n"
        "Say 'remind me <time>' to set reminders\n"
        "Reply /remind_msg <time> <text> to set reminder for a specific message"
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text

    if "/notes" in text:
        user_notes = notes.get(chat_id, [])
        response = "\n".join(user_notes) if user_notes else "You have no notes."
        await update.message.reply_text(response)

    elif "/weather" in text:
        city = text.replace("/weather", "").strip()
        response = await get_weather(city)
        await update.message.reply_text(response)

    elif "/translate" in text:
        parts = text.replace("/translate", "").strip().split(" ", 1)
        if len(parts) == 2:
            lang, msg = parts
            translation = await translate_text(msg, lang)
            await update.message.reply_text(translation)
        else:
            await update.message.reply_text("Usage: /translate <language_code> <text>")

    elif text.lower().startswith("remind me"):
        parsed_time = dateparser.parse(text)
        if parsed_time:
            reminders.setdefault(chat_id, []).append((parsed_time, text))
            await update.message.reply_text(f"Reminder set for {parsed_time}!")
        else:
            await update.message.reply_text("Couldn't parse time.")

    elif update.message.reply_to_message and text.lower() == "note this":
        note = update.message.reply_to_message.text
        notes.setdefault(chat_id, []).append(note)
        await update.message.reply_text("Note saved!")

    elif "/remind_msg" in text and update.message.reply_to_message:
        parts = text.replace("/remind_msg", "").strip().split(" ", 1)
        if len(parts) == 2:
            time_str, reminder_text = parts
            parsed_time = dateparser.parse(time_str)
            if parsed_time:
                reminders.setdefault(chat_id, []).append((parsed_time, reminder_text, update.message.reply_to_message.message_id))
                await update.message.reply_text(f"Reminder set for {parsed_time}!")
            else:
                await update.message.reply_text("Couldn't parse reminder time.")
        else:
            await update.message.reply_text("Usage: /remind_msg <time> <text>")

async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    now = datetime.datetime.now()
    for chat_id, reminder_list in reminders.items():
        reminders_to_remove = []
        for reminder in reminder_list:
            reminder_time = reminder[0]
            reminder_text = reminder[1]
            message_id = reminder[2] if len(reminder) > 2 else None

            if now >= reminder_time:
                try:
                    if message_id:
                        await bot.send_message(chat_id, f"Reminder: {reminder_text}", reply_to_message_id=message_id)
                    else:
                        await bot.send_message(chat_id, f"Reminder: {reminder_text}")
                except Exception as e:
                    print(f"Reminder sending error: {e}")
                reminders_to_remove.append(reminder)

        for rem in reminders_to_remove:
            reminder_list.remove(rem)

# Flask Webhook
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    if data:
        update = Update.de_json(data, bot)
        asyncio.run(application.process_update(update))
    return "OK"

# Initialize bot and application
bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Add job to check reminders every 60 seconds
application.job_queue.run_repeating(check_reminders, interval=60)

# Main
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
