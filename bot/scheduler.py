import asyncio
import datetime


async def send_reminder(bot, chat_id, text, delay_seconds):
    await asyncio.sleep(delay_seconds)
    await bot.send_message(chat_id, text)

async def reminder_loop(bot):
    while True:
        reminders = get_all_reminders()
        now = datetime.datetime.now()

        for reminder in reminders:
            reminder_time = datetime.datetime.fromisoformat(reminder["time"])
            if now >= reminder_time:
                try:
                    await bot.send_message(
                        chat_id=reminder["chat_id"],
                        text=f"🔔 Reminder: {reminder['text']}"
                    )
                    delete_reminder(reminder["id"])  # remove after sending
                except Exception as e:
                    print(f"Reminder send failed: {e}")
        await asyncio.sleep(60)  # Check every minute

