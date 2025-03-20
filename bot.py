from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# Fetch Interaction GIFs
def fetch_interaction_gif(action):
    url = f"https://api.waifu.pics/sfw/{action}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["url"]
    else:
        return {"error": "Could not fetch interaction GIF."}

# Fetch Anime Images
def fetch_anime_image(category="waifu"):
    url = f"https://api.waifu.pics/sfw/{category}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["url"]
    else:
        return {"error": "Could not fetch anime image."}

# Fetch Anime Texts
def fetch_anime_text(endpoint):
    url = f"https://api.waifu.it/api/{endpoint}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["text"]
    else:
        return {"error": "Could not fetch anime text."}

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "✨ **Welcome to the Anime Bot!**\n\n"
        "Use the following commands:\n"
        "🎭 /interaction <type> - Get a random interaction GIF (e.g., hug, slap, dance).\n"
        "🖼️ /anime_image <category> - Get a random anime image (e.g., waifu, husbando).\n"
        "📜 /anime_text <type> - Get random anime text (e.g., fact, quote, owoify)."
    )

# Command: Interactions
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

# Command: Anime Images
async def anime_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    category = "waifu"
    if context.args:
        category = context.args[0].lower()
    image_url = fetch_anime_image(category)
    if "error" in image_url:
        await update.message.reply_text("Sorry, I couldn't fetch the anime image. Please try again later!")
    else:
        await update.message.reply_photo(photo=image_url, caption=f"Here's a {category.capitalize()} image for you!")

# Command: Anime Texts
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

# Main function
def main():
    application = Application.builder().token("6438781804:AAGvcF5pp2gg2Svr5f0kpxvG9ZMoiG1WACc").build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("interaction", interaction))
    application.add_handler(CommandHandler("anime_image", anime_image))
    application.add_handler(CommandHandler("anime_text", anime_text))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
