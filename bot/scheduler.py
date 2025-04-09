import asyncio

async def send_reminder(bot, chat_id, text, delay_seconds):
    await asyncio.sleep(delay_seconds)
    await bot.send_message(chat_id, text)
# Scheduled reminders
