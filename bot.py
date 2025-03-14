import os
import requests
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configuration
BOT_TOKEN = "6438781804:AAGvcF5pp2gg2Svr5f0kpxvG9ZMoiG1WACc"
DOWNLOAD_DIR = "/home/nikhil/downloads"
NGINX_BASE_URL = "http://172.191.165.71"  # Update this with your server IP or domain

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ensure the download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Send me a direct link to download the file!")

def download_file(update: Update, context: CallbackContext) -> None:
    url = update.message.text

    try:
        # Extract filename from URL
        filename = url.split("/")[-1]
        file_path = os.path.join(DOWNLOAD_DIR, filename)

        # Download the file
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            # Send the direct link to the user
            file_link = f"{NGINX_BASE_URL}/{filename}"
            update.message.reply_text(f"Download complete! Access your file: {file_link}")
        else:
            update.message.reply_text("Failed to download the file. Please check the link.")

    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        update.message.reply_text("An error occurred while downloading the file.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_file))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
