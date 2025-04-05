
import os
import telegram
from telegram.ext import filters as Filters
from flask import Flask, request
import asyncio
from anthropic import AsyncAnthropic
import requests
from googletrans import Translator
import datetime
import dateparser

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

if not BOT_TOKEN or not CLAUDE_API_KEY or not WEATHER_API_KEY:
    raise ValueError("Missing API keys.")

anthropic = AsyncAnthropic(api_key=CLAUDE_API_KEY)
translator = Translator()

bot = telegram.Bot(token=BOT_TOKEN)
app = Flask(__name__)

notes = {}
reminders = {}

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

async def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()
        if response["cod"] != "404":
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

async def translate_text(text, target_language):
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        print(f"Translation Error: {e}")
        return "Translation unavailable."

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
    for chat_id, reminder_list in reminders.items():
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

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Bot is alive! ✅", 200

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
                ai_response = None

            if ai_response:
                asyncio.run(bot.send_message(chat_id=chat_id, text=ai_response))
    return "OK", 200

async def reminder_loop():
    while True:
        await check_reminders()
        await asyncio.sleep(60)

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: asyncio.run(reminder_loop())).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
