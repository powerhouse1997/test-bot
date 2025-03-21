from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import requests
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for webhook
app = Flask(__name__)

# Bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("Missing BOT_TOKEN environment variable")

# Create the Telegram bot application
application = Application.builder().token(BOT_TOKEN).build()

# Fetch Interaction GIFs
def fetch_interaction_gif(action):
    url = f"https://api.waifu.pics/sfw/{action}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["url"]
    else:
        logger.error("Failed to fetch interaction GIF.")
        return {"error": "Could not fetch interaction GIF."}

# Fetch Anime Images
def fetch_anime_image(category="waifu"):
    url = f"https://api.waifu.pics/sfw/{category}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["url"]
    else:
        logger.error("Failed to fetch anime image.")
        return {"error": "Could not fetch anime image."}

# Fetch Anime Texts
def fetch_anime_text(endpoint):
    url = f"https://api.waifu.it/api/{endpoint}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["text"]
    else:
        logger.error("Failed to fetch anime text.")
        return {"error": "Could not fetch anime text."}

# Telegram bot command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "✨ **Welcome to the Anime Bot!**\n\n"
        "Use the following commands:\n"
        "🎭 /interaction <type> - Get a random interaction GIF (e.g., hug, slap, dance).\n"
        "🖼️ /anime_image <category> - Get a random anime image (e.g., waifu, husbando).\n"
        "📜 /anime_text <type> - Get random anime text (e.g., fact, quote, owoify)."
    )

async def interaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Please provide an interaction type! Example: /interaction hug")
        return
    action = context.args[0].lower()
    gif_url = fetch_interaction_gif(action)
    if "error" in gif_url:
        await update.message.reply_text("Sorry, I couldn't fetch the interaction GIF. Please try again later!")
    else:
        await update.message.reply_animation(animation=gif_url, caption=f"Here's a {action} GIF for you!")

async def anime_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    category = "waifu"
    if context.args:
        category = context.args[0].lower()
    image_url = fetch_anime_image(category)
    if "error" in image_url:
        await update.message.reply_text("Sorry, I couldn't fetch the anime image. Please try again later!")
    else:
        await update.message.reply_photo(photo=image_url, caption=f"Here's a {category.capitalize()} image for you!")

async def anime_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Please provide a text type! Example: /text fact")
        return
    endpoint = context.args[0].lower()
    text_content = fetch_anime_text(endpoint)
    if "error" in text_content:
        await update.message.reply_text("Sorry, I couldn't fetch the anime text. Please try again later!")
    else:
        await update.message.reply_text(f"Here's a random {endpoint.capitalize()}:\n\n{text_content}")

# Register bot command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("interaction", interaction))
application.add_handler(CommandHandler("anime_image", anime_image))
application.add_handler(CommandHandler("anime_text", anime_text))

# Flask route for webhook
@app.route('/', methods=['GET'])
def webhook():
    try:
        update_data = request.get_json(force=True)
        logger.info(f"Webhook received: {update_data}")
        update = Update.de_json(update_data, application.bot)
        application.process_update(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
