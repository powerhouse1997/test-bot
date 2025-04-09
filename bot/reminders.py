import json
import os
import asyncio
import datetime
# bot/reminders.py
from bot.models import get_favorites

async def reminder_loop(bot):
    while True:
        print("🔎 Checking for new manga releases...")
        
        # Example: Notify all users about a fake new chapter
        # In real, you should integrate MangaDex / other API
        users = [12345678]  # Fake user ID list
        for user_id in users:
            favorites = get_favorites(user_id)
            for manga in favorites:
                await bot.send_message(user_id, text=f"🔥 New chapter released for '{manga}'!")
        
        await asyncio.sleep(3600)  # Sleep 1 hour


REMINDERS_FILE = "reminders.json"
reminders = {}

def save_reminders():
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f)

def load_reminders():
    global reminders
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r") as f:
            reminders.update(json.load(f))

async def reminder_loop(bot):
    while True:
        now = datetime.datetime.now()
        for chat_id, items in list(reminders.items()):
            to_remove = []
            for reminder_time, text, *msg_id in items:
                reminder_dt = datetime.datetime.fromisoformat(reminder_time)
                if now >= reminder_dt:
                    try:
                        if msg_id:
                            await bot.send_message(chat_id=chat_id, text=f"Reminder: {text}", reply_to_message_id=msg_id[0])
                        else:
                            await bot.send_message(chat_id=chat_id, text=f"Reminder: {text}")
                    except Exception as e:
                        print(f"Send error: {e}")
                    to_remove.append((reminder_time, text, *msg_id))
            for r in to_remove:
                items.remove(r)
        save_reminders()
        await asyncio.sleep(60)
