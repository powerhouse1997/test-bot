from . import utils, reminders, database, groq

async def handle_update(update, bot):
    from bot.database import todos  # moved inside to avoid circular import
    chat_id = update.effective_chat.id

    if update.message:
        text = update.message.text or ""

        if text.startswith("/start"):
            await bot.send_message(chat_id=chat_id, text="Hello! I'm your Personal Assistant 🚀\nI can help you with reminders, todos, weather, AI questions, and more!")
            database.save_user(chat_id)

        elif text.startswith("/weather"):
            city = text.replace("/weather", "").strip()
            if city:
                weather_info = await utils.get_weather(city)
                await bot.send_message(chat_id=chat_id, text=weather_info)
            else:
                await bot.send_message(chat_id=chat_id, text="❗ Please provide a city name. Example: /weather London")

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
            todos_list = database.get_todos(chat_id)
            if todos_list:
                message = "🗒️ Your To-Dos:\n\n"
                for idx, item in enumerate(todos_list, start=1):
                    message += f"{idx}. {item['task']}\n"
                await bot.send_message(chat_id=chat_id, text=message)
            else:
                await bot.send_message(chat_id=chat_id, text="🎉 You have no pending to-dos!")

        elif text.startswith("/done"):
            try:
                index = int(text.replace("/done", "").strip()) - 1
                database.complete_todo(chat_id, index)
                await bot.send_message(chat_id=chat_id, text="✅ Marked as done!")
            except (ValueError, IndexError):
                await bot.send_message(chat_id=chat_id, text="❗ Please provide a valid task number. Example: /done 1")

        elif text.startswith("/summary"):
            await send_daily_summary(chat_id, bot)

        elif text.startswith("/ask"):
            query = text.replace("/ask", "").strip()
            if query:
                await bot.send_message(chat_id=chat_id, text="🤔 Thinking...")
                reply = await groq.ask_groq(query)
                await bot.send_message(chat_id=chat_id, text=reply)
            else:
                await bot.send_message(chat_id=chat_id, text="❗ Please provide a question after /ask")

async def send_daily_summary(chat_id, bot):
    # Weather
    weather_info = await utils.get_weather("Your Default City")  # (Optional: make dynamic per user)

    # Todos
    todos_list = database.get_todos(chat_id)
    if todos_list:
        todos_message = "\n".join([f"- {item['task']}" for item in todos_list])
    else:
        todos_message = "🎉 No tasks for today!"

    message = f"🌤️ Weather:\n{weather_info}\n\n🗒️ To-Dos:\n{todos_message}"
    await bot.send_message(chat_id=chat_id, text=message)
