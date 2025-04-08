from . import utils, reminders, database, groq
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def handle_update(update, bot):
    from bot.database import todos  # move inside to avoid cyclic imports
    chat_id = update.effective_chat.id

    if update.message:
        text = update.message.text or ""

        if text.startswith("/start"):
            await bot.send_message(
                chat_id=chat_id,
                text="👋 Hello! Welcome to *YourBotName*.\n\nHere’s what I can do for you:\n\n"
                     "• /ask - Talk with AI 🤖\n"
                     "• /weather - Get current weather 🌦️\n"
                     "• /summary - Daily summary 📋\n\n"
                     "Click the buttons below to get started!",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💬 Ask AI", callback_data="ask_ai")],
                    [InlineKeyboardButton("🌦️ Get Weather", callback_data="get_weather")],
                    [InlineKeyboardButton("📋 View Summary", callback_data="view_summary")],
                ])
            )

            
            keyboard = [
                [
                    InlineKeyboardButton("📋 Show my Todos", callback_data="show_todos"),
                    InlineKeyboardButton("⏰ Set Reminder", callback_data="set_reminder")
                ],
                [
                    InlineKeyboardButton("💬 Chat with AI", callback_data="chat_ai")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await bot.send_message(
                chat_id=chat_id,
                text="👋 *Welcome to Personal Assistant Bot!*\n\nChoose an option below to get started:",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            database.save_user(chat_id)

        elif text.startswith("/weather"):
            city = text.replace("/weather", "").strip()

            if not city:
                # Try to get user's saved location
                city = "Mumbai"
                if not city:
                    await bot.send_message(chat_id=chat_id, text="📍 Please send me your location to get weather info.")
                    return

            await bot.send_chat_action(chat_id=chat_id, action="typing")
            weather_info = utils.get_weather(city)
            await bot.send_message(chat_id=chat_id, text=weather_info)

        elif text.startswith("/remindme"):
            reminder_text = text.replace("/remindme", "").strip()
            reminder_time = utils.parse_reminder_time(reminder_text)

            if reminder_time:
                database.add_reminder(chat_id, reminder_time.isoformat(), reminder_text)
                await bot.send_message(chat_id=chat_id, text=f"⏰ Reminder set for {reminder_time}!")
            else:
                await bot.send_message(chat_id=chat_id, text="❌ I couldn't understand the time you provided.")

        elif text.startswith("/todo"):
            task = text.replace("/todo", "").strip()
            if task:
                database.add_todo(chat_id, task)
                await bot.send_message(chat_id=chat_id, text=f"📝 Added task:\n➡️ {task}")
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
                await bot.send_message(chat_id=chat_id, text="❗ Invalid task number.")

        elif text.startswith("/summary"):
            await send_daily_summary(chat_id, bot)

        elif text.startswith("/ask"):
            prompt = text.replace("/ask", "").strip()
            if prompt:
                await bot.send_chat_action(chat_id=chat_id, action="typing")
                reply = await groq.ask_ai(prompt)
                await bot.send_message(chat_id=chat_id, text=f"🤖 *AI Reply:*\n\n{reply}", parse_mode="Markdown")
            else:
                await bot.send_message(chat_id=chat_id, text="❗ Please provide a prompt.")

        else:
            # Normal user message (auto reply with AI)
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            reply = await groq.ask_ai(text)
            await bot.send_message(chat_id=chat_id, text=f"🤖 *AI Reply:*\n\n{reply}", parse_mode="Markdown")

    elif update.callback_query:
        query = update.callback_query
        data = query.data

        if data == "show_todos":
            await show_todos(chat_id, bot)
        elif data == "set_reminder":
            await bot.send_message(chat_id=chat_id, text="⏰ Type `/remindme 10 min Meeting` to set a reminder!")
        elif data == "chat_ai":
            await bot.send_message(chat_id=chat_id, text="💬 Ask me anything!")

async def show_todos(chat_id, bot):
    todos_list = database.get_todos(chat_id)
    if todos_list:
        message = "📝 *Your To-Do List:*\n\n"
        for idx, item in enumerate(todos_list, start=1):
            message += f"{idx}. {item['task']}\n"
    else:
        message = "🎉 You have no pending to-dos!"
    await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

async def send_daily_summary(chat_id, bot):
    weather_info = utils.get_weather("Mumbai")  # You can store per user if needed
    todos_list = database.get_todos(chat_id)

    if todos_list:
        todos_message = "\n".join([f"• {item['task']}" for item in todos_list])
    else:
        todos_message = "🎉 No tasks for today!"

    message = (
        "🗓️ *Daily Summary*\n\n"
        f"🌤️ *Weather:*\n{weather_info}\n\n"
        f"📝 *To-Dos:*\n{todos_message}"
    )
    await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
