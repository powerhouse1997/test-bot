import logging
import os
import asyncio
from flask import Flask, request, Response

import cloudinary
import cloudinary.uploader
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- SECURELY LOAD CREDENTIALS FROM ENVIRONMENT VARIABLES ---
try:
    TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
    CLOUDINARY_CLOUD_NAME = os.environ['CLOUDINARY_CLOUD_NAME']
    CLOUDINARY_API_KEY = os.environ['CLOUDINARY_API_KEY']
    CLOUDINARY_API_SECRET = os.environ['CLOUDINARY_API_SECRET']
    # A secret token to ensure requests are from Telegram (optional but recommended)
    WEBHOOK_SECRET_TOKEN = os.environ.get('WEBHOOK_SECRET_TOKEN', 'a_default_secret')

except KeyError as e:
    logging.critical(f"FATAL ERROR: Environment variable {e} is not set.")
    exit()

# --- Cloudinary Configuration ---
cloudinary.config(
  cloud_name = CLOUDINARY_CLOUD_NAME,
  api_key = CLOUDINARY_API_KEY,
  api_secret = CLOUDINARY_API_SECRET,
  secure = True
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- BOT HANDLER FUNCTIONS (These remain mostly the same!) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Hello! Send me a photo. I will use AI to upscale it and send it back as a file.'
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Processing your image with maximum AI upscale, please wait...")
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        logger.info("Photo downloaded from Telegram.")
        upload_result = cloudinary.uploader.upload(photo_bytes)
        logger.info("Photo uploaded to Cloudinary.")
        public_id = upload_result.get('public_id')
        original_format = upload_result.get('format', 'jpg')
        upscaled_url = cloudinary.CloudinaryImage(public_id).build_url(
            transformation=[
                {'effect': "upscale"},
                {'quality': "auto"}
            ]
        )
        logger.info(f"Generated upscaled URL: {upscaled_url}")
        await update.message.reply_document(
            document=upscaled_url,
            caption="Here's your maximum-AI upscaled image! (Sent as a file to prevent quality loss)",
            filename=f"upscaled_{public_id}.{original_format}"
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await update.message.reply_text("Sorry, I couldn't process your image right now. Please try again.")


# --- CORE WEBHOOK LOGIC ---
# Initialize the bot application
ptb_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
ptb_app.add_handler(CommandHandler("start", start))
ptb_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# Initialize the Flask web server
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    # A simple page to confirm the server is running
    return "Hello, I am the upscaler bot's webhook listener!"

@flask_app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
async def telegram_webhook():
    # Check for a secret token to verify the request is from Telegram
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET_TOKEN:
        return Response("Unauthorized", status=403)
        
    # Process the update from Telegram
    update_data = request.get_json()
    update = Update.de_json(data=update_data, bot=ptb_app.bot)
    
    # Let the python-telegram-bot library handle the update
    await ptb_app.process_update(update)
    
    # Return an empty 200 OK response to Telegram
    return Response("OK", status=200)

# Note: We do not run the Flask app directly here.
# A production WSGI server like Gunicorn will be used to run `flask_app`.
