import asyncio
from datetime import datetime, time, timedelta

async def daily_summary(bot, database):
    while True:
        now = datetime.now()
        target_time = time(8, 0)  # 8:00 AM

        # Find out how many seconds to wait
        next_run = datetime.combine(now.date(), target_time)
        if now.time() > target_time:
            next_run += timedelta(days=1)

        wait_seconds = (next_run - now).total_seconds()
        print(f"Next summary scheduled in {wait_seconds / 3600:.2f} hours.")

        await asyncio.sleep(wait_seconds)

        # Fetch all users and send summaries
        all_chat_ids = database.get_all_users()
        for chat_id in all_chat_ids:
            await send_summary_to_user(bot, chat_id)

        # Sleep a bit before checking again
        await asyncio.sleep(60)

async def send_summary_to_user(bot, chat_id):
    from .handlers import send_daily_summary  # Import inside function to avoid circular import
    await send_daily_summary(chat_id, bot)
