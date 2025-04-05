from . import utils, reminders

async def handle_update(update, bot):
    chat_id = update.effective_chat.id

    if update.message:
        text = update.message.text or ""

        if text == "/start":
            await bot.send_message(chat_id=chat_id, text="Hello, I'm alive! 🚀")
        elif "/weather" in text:
            city = text.replace("/weather", "").strip()
            weather_info = await utils.get_weather(city)
            await bot.send_message(chat_id=chat_id, text=weather_info)
        elif "/translate" in text:
            parts = text.replace("/translate", "").strip().split(" ", 1)
            if len(parts) == 2:
                lang, txt = parts
                translation = await utils.translate_text(txt, lang)
                await bot.send_message(chat_id=chat_id, text=translation)
        elif "remind me" in text.lower():
            reminder_time = await utils.parse_reminder_time(text)
            if reminder_time:
                reminders.reminders.setdefault(str(chat_id), []).append((reminder_time.isoformat(), text))
                reminders.save_reminders()
                await bot.send_message(chat_id=chat_id, text=f"Reminder set for {reminder_time}!")
