from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import requests

TOKEN = os.environ.get("BOT_TOKEN", "6438781804:AAGvcF5pp2gg2Svr5f0kpxvG9ZMoiG1WACc")
WEBHOOK_URL = "https://animebot-cngyfvg2bqadd0ea.centralus-01.azurewebsites.net/webhook"

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# Command: Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to the Anime Bot! 😊")

# Command: Interaction
async def interaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Please provide an interaction type! Example: /interaction hug")
        return
    action = context.args[0].lower()
    gif_url = fetch_interaction_gif(action)
    if "error" in gif_url:
        await update.message.reply_text("Sorry, I couldn't fetch the interaction GIF.")
    else:
        await update.message.reply_animation(animation=gif_url, caption=f"Here's a {action} GIF for you!")

# Utility Functions
def fetch_interaction_gif(action):
    url = f"https://api.waifu.pics/sfw/{action}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["url"]
    else:
        return {"error": "Could not fetch interaction GIF."}

# Add Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("interaction", interaction))

# Webhook Route
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), application.bot)
        application.process_update(update)
        return 'OK', 200
    except Exception as e:
        print(f"Error processing update: {e}")
        return 'Internal Server Error', 500

# Set Webhook
def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    response = requests.post(url, json={"url": WEBHOOK_URL})
    print(response.json())

# Start the App
if __name__ == "__main__":
    set_webhook()
    app.run(host='0.0.0.0', port=8000)
