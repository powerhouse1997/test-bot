import os
import telegram
from telegram.ext import CallbackContext
from flask import Flask, request
import asyncio
from anthropic import AsyncAnthropic
import requests
from deep_translator import GoogleTranslator
import datetime
import dateparser

# Load environment variables
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

if not BOT_TOKEN or not CLAUDE_API_KEY or not WEATHER_API_KEY:
    raise ValueError("Missing API keys.")

# Initialize services
anthropic = AsyncAnthropic(api_key=CLAUDE_API_KEY)
bot = telegram.Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Storage
notes = {}
reminders = {}

# Claude AI Response
async def get_ai_response_claude(user_message):
    try:
        message = await anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f"Claude API Error: {e}")
        return "Sorry, I encountered a Claude API error."

# Weather
async def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") != "404":
            main = response["main"]
            temperature = main["temp"]
            humidity = main["humidity"]
            description = response["weather"][0]["description"]
            return f"Weather in {city}: {description}, Temperature: {temperature}°C, Humidity: {humidity}%"
        else:
            return "City not found."
    except Exception as e:
        print(f"Weather API Error: {e}")
        return "Weather information unavailable."

# Translator
async def translate_text(text, target_language):
    try:
        translation = GoogleTranslator(source='auto', target=target_language).translate(text)
        return translation
    except Exception as e:
        print(f"Translation Error: {e}")
        return "Translation unavailable."

# Notes
async def add_note(chat_id, note_text):
    if chat_id not in notes:
        notes[chat_id] = []
    notes[chat_id].append(note_text)
    return "Note added!"

async def get_notes(chat_id):
    if chat_id in notes and notes[chat_id]:
        return "\n".join(notes[chat_id])
    else:
        return "No notes found."

# Reminders
async def add_reminder_natural(chat_id, reminder_text):
    parsed_date = dateparser.parse(reminder_text)
    if parsed_date:
        if chat_id not in reminders:
            reminders[chat_id] = []
        reminders[chat_id].append((parsed_date, reminder_text))
        return f"Reminder set for {parsed_date}!"
    else:
        return "Sorry, I couldn't understand the time. Please try again."

async def add_reminder_to_message(chat_id, reminder_time, reminder_text, message_id):
    try:
        reminder_datetime = dateparser.parse(reminder_time)
        if reminder_datetime:
            if chat_id not in reminders:
                reminders[chat_id] = []
            reminders[chat_id].append((reminder_datetime, reminder_text, message_id))
            return f"Reminder set for {reminder_datetime}!"
        else:
            return "Sorry, I couldn't understand the time. Please try again."
    except Exception as e:
        print(f"Reminder Error: {e}")
        return "Sorry, there was an error setting the reminder."

async def check_reminders():
    now = datetime.datetime.now()
    for chat_id, reminder_list in list(reminders.items()):
        reminders_to_remove = []
        for reminder_time, reminder_text, *message_id in reminder_list:
            if now >= reminder_time:
                try:
                    if message_id:
                        await bot.send_message(chat_id=chat_id, text=f"Reminder: {reminder_text}", reply_to_message_id=message_id[0])
                    else:
                        await bot.send_message(chat_id=chat_id, text=f"Reminder: {reminder_text}")
                except telegram.error.BadRequest:
                    await bot.send_message(chat_id=chat_id, text=f"Reminder: {reminder_text} (Original message not found)")
                reminders_to_remove.append((reminder_time, reminder_text, *message_id))
        for reminder in reminders_to_remove:
            reminder_list.remove(reminder)

# Sending message
async def send_telegram_message(chat_id, text):
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except telegram.error.TelegramError as e:
        print(f"Error sending message to {chat_id}: {e}")

# Flask webhook
@app.route("/", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.effective_chat.id
    if update.message:
        if update.message.text:
            user_message = update.message.text
            if "/notes" in user_message:
                ai_response = asyncio.run(get_notes(chat_id))
            elif "remind me" in user_message.lower():
                ai_response = asyncio.run(add_reminder_natural(chat_id, user_message))
            elif "/remind_msg" in user_message:
                parts = user_message.replace("/remind_msg", "").strip().split(" ", 1)
                if len(parts) == 2 and update.message.reply_to_message:
                    reminder_time, reminder_text = parts
                    ai_response = asyncio.run(add_reminder_to_message(chat_id, reminder_time, reminder_text, update.message.reply_to_message.message_id))
                else:
                    ai_response = "Usage: Reply to a message with /remind_msg <time> <reminder_text>"
            elif "/weather" in user_message:
                city = user_message.replace("/weather", "").strip()
                ai_response = asyncio.run(get_weather(city))
            elif "/translate" in user_message:
                parts = user_message.replace("/translate", "").strip().split(" ", 1)
                if len(parts) == 2:
                    target_language, text = parts
                    ai_response = asyncio.run(translate_text(text, target_language))
                else:
                    ai_response = "Usage: /translate <language code> <text>"
            elif update.message.reply_to_message and user_message.lower() == 'note this':
                note_text = update.message.reply_to_message.text
                ai_response = asyncio.run(add_note(chat_id, note_text))
            else:
                pass  # Do nothing

            if 'ai_response' in locals():
                asyncio.run(send_telegram_message(chat_id, ai_response))
        elif update.message.document:
            pass  # Handle documents if needed
    return "OK"

# Reminder loop
async def reminder_loop():
    while True:
        await check_reminders()
        await asyncio.sleep(60)

# Startup code for Railway / Production
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(reminder_loop())
    # DO NOT run app.run(), Railway will use Gunicorn to run the app
