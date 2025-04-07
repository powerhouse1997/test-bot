from . import utils, reminders, database, groq

async def handle_update(update, bot):
    from bot.database import todos  # moved inside to avoid cyclic import
    chat_id = update.effective_chat.id

    if update.message:
        text = update.message.text or ""

        if text.startswith("/start"):
            await bot.send_message(
                chat_id=chat_id,
                text="👋 Hello! I'm your Personal Assistant 🚀\n\nI can help you with:\n- Reminders\n- To-Dos\n- Weather\n- Chatting with AI\n\nType /help to see all commands!"
            )
            database.save_user(chat_id)

        elif text.startswith("/weather"):
            city = text.replace("/weather", "").strip()
            if not city:
                await bot.send_message(chat_id=chat_id, text="🌍 Please provide a city name after /weather.")
                return

            await bot.send_chat_action(chat_id=chat_id, action="typing")
            weather_info = await utils.get_weather(city)
            await bot.send_message(chat_id=chat_id, text=weather_info)

        elif text.startswith("/remindme"):
            reminder_text = text.replace("/remindme", "").strip()
            reminder_time = await utils.parse_reminder_time(reminder_text)
            if reminder_time:
                database.add_reminder(chat_id, reminder_time.isoformat(), reminder_text)
                await bot.send_message(chat_id=chat_id, text=f"⏰ Reminder set for {reminder_time}!")
            else:
                await bot.send_message(chat_id=chat_id, text="❌ Sorry, I couldn't understand the reminder time.")

        elif text.startswith("/todo"):
            task = text.replace("/todo", "").strip()
            if task:
                database.add_todo(chat_id, task)
                await bot.send_message(chat_id=chat_id, text=f"📝 Added to your to-do list:\n\n➡️ {task}")
            else:
                await bot.send_message(chat_id=chat_id, text="❗ Please provide a task after /todo.")

        elif text.startswith("/show_todos"):
            todos_list = database.get_todos(chat_id)
            if todos_list:
                message = "🗒️ *Your To-Do List:*\n\n"
                for idx, item in enumerate(todos_list, start=1):
                    message += f"{idx}. {item['task']}\n"
                await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            else:
                await bot.send_message(chat_id=chat_id, text="🎉 You have no pending to-dos!")

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
            prompt = text.replace("/ask", "").strip()
            if prompt:
                await bot.send_chat_action(chat_id=chat_id, action="typing")
                reply = await groq.ask_ai(prompt)
                await bot.send_message(chat_id=chat_id, text=f"🤖 *AI Reply:*\n\n{reply}", parse_mode="Markdown")
            else:
                await bot.send_message(chat_id=chat_id, text="❗ Please provide a question after /ask.")

        else:
            # If it's not a command (default case), send normal text to AI
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            reply = await groq.ask_ai(text)
            await bot.send_message(chat_id=chat_id, text=f"🤖 *AI Reply:*\n\n{reply}", parse_mode="Markdown")


async def send_daily_summary(chat_id, bot):
    # Weather
    weather_info = await utils.get_weather("Your Default City")  # TODO: Replace with user's city

    # Todos
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
