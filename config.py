import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Chat ID (for auto-news)
CHAT_ID = os.getenv("CHAT_ID")
