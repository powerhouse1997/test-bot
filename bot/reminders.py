# bot/reminders.py

import asyncio
import logging

async def reminder_loop(bot):
    while True:
        try:
            # 🔔 Send a reminder message (you can make this smarter later)
            # For now just log
            logging.info("🔔 Running reminder loop... (you can add manga updates here)")
            
            # Example: Send a message to a hardcoded chat_id (replace with your own)
            # await bot.send_message(chat_id=123456789, text="Don't forget to read your manga today!")

            await asyncio.sleep(3600)  # Wait for 1 hour before next reminder
        except Exception as e:
            logging.error(f"Error in reminder loop: {e}")
            await asyncio.sleep(10)  # Wait before retrying in case of error
