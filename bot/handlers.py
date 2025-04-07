from . import utils, reminders, database, groq
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

async def handle_update(update, bot):
    from bot.database import todos  # move inside to avoid circular import
    chat_id = update.effective_chat.id

    if update.message:
        text = update.message.text or ""

        if text.startswith("/start"):
            keyboard = [
                [InlineKeyboardButton("📝 Show My Todos", callback_data="show_todos")],
                [InlineKeyboardButton("⏰ Set Reminder", callback_data="set_reminder")],
                [InlineKeyboardButton("🌤️ Weather", callback_data="weather")],
                [InlineKeyboardButton("🧠 Ask AI", callback_data="ask_ai")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await bot.send_message(
                chat_id=chat_id,
                text="👋 Hello! I'm your Personal Assistant bot 🚀\n\nChoose an action below:",
                reply_markup=reply_markup
            )
            database.save_user(chat_id)

        elif text.startswith("/weather"):
            keyboard = [
                [KeyboardButton("📍 Share Location", request_location=True)],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await bot.send_message(chat_id=chat_id, text="Please share your location 🌍", reply_markup=reply_markup)

        elif update.message.location:
            lat = update.message.location.latitude
            lon = update.message.location.longitude
            city = await utils.get_city_from_location(lat, lon)
            weather_info = await utils.get_weather(city)
            await bot.send_message(chat_id=chat_id, text=f"🌦️ Weather in {city}:\n{weather_info}")

        elif text.startswith("/remindme"):
            reminder_text = text.replace("/remindme", "").strip()
            reminder_time = await utils.parse_reminder_time(reminder_text)
            if reminder_time:
                database.add_reminder(chat_id, reminder_time.isoformat(), reminder_text)
                await bot.send_message(chat_id=chat_id, text=f"✅ Reminder set for {reminder_time}!")
            else:
                await bot.send_message(chat_id=chat_id, text="❌ Sorry, I couldn't understand the reminder time.")

        elif text.startswith("/todo"):
            task = text.replace("/todo", "").strip()
            if task:
                database.add_todo(chat_id, task)
                await bot.send_message(chat_id=chat_id, text=f"📝 Added to your to-do list: {task}")
            else:
                await bot.send_message(chat_id=chat_id, text="❗ Please provide a task after /todo.")

        elif text.startswith("/show_todos"):
            await show_todos(chat_id, bot)

        elif text.startswith("/done"):
            try:
                index = int(text.replace("/done", "").strip()) - 1
                database.complete_todo(chat_id, index)
                await bot.send_message(chat_id=chat_id, text="✅ Marked as done!")
            except (ValueError, IndexError):
                await bot.send_message(chat_id=chat_id, text="❗ Please provide a valid task number (e.g., /done 1)")

        elif text.startswith("/summary"):
            await send_daily_summary(chat_id, bot)

        elif text.startswith("/ask"):
            question = text.replace("/ask", "").strip()
            if question:
                await bot.send_chat_action(chat_id=chat_id, action="typing")
                reply = await groq.ask_ai(question)
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"🧠 *Here’s what I think:*\n\n{reply}",
                    parse_mode="Markdown"
                )
            else:
                await bot.send_message(chat_id=chat_id, text="❓ Please ask something after /ask.")

    elif update.callback_query:
        query = update.callback_query
        data = query.data

        if data == "show_todos":
            await show_todos(chat_id, bot)
        elif data == "set_reminder":
            await bot.send_message(chat_id=chat_id, text="📝 Use /remindme to set a reminder!\nExample: `/remindme Meeting at 3pm`", parse_mode="Markdown")
        elif data == "weather":
            await bot.send_message(chat_id=chat_id, text="🌍 Use /weather to get weather updates!")
        elif data == "ask_ai":
            await bot.send_message(chat_id=chat_id, text="🤖 Use /ask followed by your question.\nExample: `/ask What's the weather on Mars?`", parse_mode="Markdown")

async def show_todos(chat_id, bot):
    todos_list = database.get_todos(chat_id)
    if todos_list:
        message = "🗒️ *Your To-Do List:*\n\n"
        for idx, item in enumerate(todos_list, start=1):
            message += f"{idx}. {item['task']}\n"
    else:
        message = "🎉 You have no pending to-dos!"
    await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

async def send_daily_summary(chat_id, bot):
    weather_info = await utils.get_weather("Your Default City")  # TODO: Get from user if needed
    todos_list = database.get_todos(chat_id)

    if todos_list:
        todos_message = "\n".join([f"✅ {item['task']}" for item in todos_list])
    else:
        todos_message = "🎉 No tasks for today!"

    message = (
        f"🌤️ *Today's Weather:*\n{weather_info}\n\n"
        f"🗒️ *Today's Tasks:*\n{todos_message}"
    )

    await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
