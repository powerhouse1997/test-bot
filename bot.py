import logging
import psutil
import shutil
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# ⚠ WARNING: Hardcoding the token is insecure. Use environment variables instead!
TOKEN = "6438781804:AAGvcF5pp2gg2Svr5f0kpxvG9ZMoiG1WACc"

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to generate a progress bar
def get_progress_bar(used, total, length=20):
    percent = used / total
    filled_length = int(length * percent)
    return "[" + "█" * filled_length + "-" * (length - filled_length) + f"] {used}/{total}MB".
