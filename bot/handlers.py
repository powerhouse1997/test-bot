from . import utils, reminders, database, groq
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import ContextTypes  # Import ContextTypes

async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from bot.database import todos  # moved inside to avoid cyclic imports
    chat_id = update.effective_chat.id

    if update.message:
        text = update.message.text or ""

        if text.startswith("/start"):
            first_name = update.effective_user.first_name

            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"👋 *Hey {first_name}! Glad to see you here!*\n\n"
                    "I'm your personal assistant, ready to help you with:\n\n"
                    "💬 *Chat with AI* — Ask me anything!\n"
                    "🌦️ *Weather Updates* — Stay ahead of the skies!\n"
                    "📝 *Manage To-Dos* — Organize your life effortlessly!\n"
                    "⏰ *Set Reminders* — Never miss anything important!\n"
                    "🗓️ *Daily Summary* — Your day at a glance!\n\n"
                    "✨ Let's get started — tap a button below!"
                ),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("💬 Chat with AI", callback_data="ask_ai"),
                        InlineKeyboardButton("🌦️ Weather", callback_data="get_weather")
                    ],
                    [
                        InlineKeyboardButton("📝 To-Dos", callback_data="show_todos"),
                        InlineKeyboardButton("⏰ Reminders", callback_data="set_reminder")
                    ],
                    [
                        InlineKeyboardButton("🗓️ Daily Summary", callback_data="view_summary")
                    ]
                ])
            )
            database.save_user(chat_id)

        elif text.startswith("/weather"):
            city = text.replace("/weather", "").strip()
            if not city:
                city = "Mumbai"  # Default city
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            weather_info = utils.get_weather(city)
            await context.bot.send_message(chat_id=chat_id, text=weather_info)

        elif text.startswith("/remindme"):
            reminder_text = text.replace("/remindme", "").strip()
            reminder_time = utils.parse_reminder_time(reminder_text)

            if reminder_time:
                database.add_reminder(chat_id, reminder_time.isoformat(), reminder_text)
                await context.bot.send_message(chat_id=chat_id, text=f"⏰ Reminder set for {reminder_time}!")
            else:
                await context.bot.send_message(chat_id=chat_id, text="❌ I couldn't understand the time you provided. Please try again.")

        elif text.startswith("/todo"):
            task = text.replace("/todo", "").strip()
            if task:
                database.add_todo(chat_id, task)
                await context.bot.send_message(chat_id=chat_id, text=f"📝 Added task:\n➡️ {task}")
            else:
                await context.bot.send_message(chat_id=chat_id, text="❗ Please provide a task after /todo.")

        elif text.startswith("/show_todos"):
            await show_todos(chat_id, context)

        elif text.startswith("/done"):
            try:
                index = int(text.replace("/done", "").strip()) - 1
                database.complete_todo(chat_id, index)
                await context.bot.send_message(chat_id=chat_id, text="✅ Marked as done!")
            except (ValueError, IndexError):
                await context.bot.send_message(chat_id=chat_id, text="❗ Invalid task number.")

        elif text.startswith("/summary"):
            await send_daily_summary(chat_id, context)

        elif text.startswith("/ask"):
            prompt = text.replace("/ask", "").strip()
            if prompt:
                await context.bot.send_chat_action(chat_id=chat_id, action="typing")
                reply = await groq.ask_ai(prompt)
                await context.bot.send_message(chat_id=chat_id, text=f"🤖 *AI Reply:*\n\n{reply}", parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=chat_id, text="❗ Please provide a prompt.")

        else:
            # Normal user message (auto AI chat reply)
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            reply = await groq.ask_ai(text)
            await context.bot.send_message(chat_id=chat_id, text=f"🤖 *AI Reply:*\n\n{reply}", parse_mode="Markdown")

    elif update.callback_query:
        query = update.callback_query
        data = query.data

        if data == "show_todos":
            await show_todos(chat_id, context)
        elif data == "set_reminder":
            await context.bot.send_message(chat_id=chat_id, text="⏰ Type `/remindme 10 min Meeting` to set a reminder!")
        elif data == "chat_ai" or data == "ask_ai":
            await context.bot.send_message(chat_id=chat_id, text="💬 Ask me anything!")
        elif data == "get_weather":
            await context.bot.send_message(chat_id=chat_id, text="🌦️ Please type `/weather CityName` to get the weather!")
        elif data == "view_summary":
            await send_daily_summary(chat_id, context)

async def show_todos(chat_id, context):
    todos_list = database.get_todos(chat_id)
    if todos_list:
        message = "📝 *Your To-Do List:*\n\n"
        for idx, item in enumerate(todos_list, start=1):
            message += f"{idx}. {item['task']}\n"
    else:
        message = "🎉 You have no pending to-dos!"
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

async def send_daily_summary(chat_id, context):
    weather_info = utils.get_weather("Mumbai")  # Default city
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
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
