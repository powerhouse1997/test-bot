import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
JIKAN_API_URL = os.getenv("JIKAN_API_URL", "https://api.jikan.moe/v4")
