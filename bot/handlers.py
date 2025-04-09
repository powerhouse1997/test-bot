from telegram import Update
from telegram.ext import ContextTypes
from bot.utils import ask_meta_ai
from bot.power_manager import is_power_user

async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        text = update.message.text or ""
        chat_id = update.effective_chat.id

        if text.startswith("/start"):
            await update.message.reply_text(
                "👋 Welcome! I am your personal assistant bot. Use /power to give me commands!"
            )
        elif text.startswith("/power"):
            if not is_power_user(update.effective_user.id):
                await update.message.reply_text("❌ You are not authorized to use /power.")
                return
            prompt = text.replace("/power", "").strip()
            if prompt:
                response = await ask_meta_ai(prompt)
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("❗ Please provide a command after /power.")
# Handlers for user commands
