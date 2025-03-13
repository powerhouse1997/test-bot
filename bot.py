import os
import psutil
import shutil
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from rich.progress import Progress
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()  
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Set up logging
logging.basicConfig(level=logging.INFO)
console = Console()

# Load Telegram Bot Token from Environment Variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Ensure Token is available
if not TOKEN:
    console.print("[bold red]Error:[/bold red] Telegram bot token is missing! Set TELEGRAM_BOT_TOKEN in environment variables.")
    exit(1)

# Function to Get System Status
def get_vm_status():
    # RAM Usage
    ram = psutil.virtual_memor
