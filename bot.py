import os
import psutil
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TOKEN = "6438781804:AAGvcF5pp2gg2Svr5f0kpxvG9ZMoiG1WACc"

# Command handlers
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I'm your bot. Use /help to see available commands.")

async def help_cmd(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("/start - Start the bot\n/help - Show commands\n/status - Get VM status")

async def status(update: Update, context: CallbackContext) -> None:
    cpu_freq = psutil.cpu_freq()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    
    status_msg = (
        f"🖥 *VM Status*\n"
        f"🔹 CPU Speed: {cpu_freq.current:.2f} MHz\n"
        f"🔹 RAM: {ram.used / (1024 ** 3):.2f} GB / {ram.total / (1024 ** 3):.2f} GB\n"
        f"🔹 Storage: {disk.used / (1024 ** 3):.2f} GB / {disk.total / (1024 ** 3):.2f} GB\n"
        f"🔹 CPU Usage: {psutil.cpu_percent()}%\n"
        f"🔹 VM Uptime: {psutil.boot_time()}"
    )

    await update.message.reply_text(status_msg, parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
