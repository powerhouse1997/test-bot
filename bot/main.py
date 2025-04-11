# bot/main.py

from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
import feedparser
import aiohttp
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn

# Load .env variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("DOMAIN")  # Example: https://your-bot.up.railway.app

# Create FastAPI app
app = FastAPI()

# Create Telegram bot application
application = ApplicationBuilder().token(TOKEN).build()

# --- Telegram Handlers ---
async def start(update: Update, context):
    await update.message.reply_text("👋 Welcome! Bot is working.")

async def get_news(update: Update, context):
    await update.message.reply_text("📰 Here’s some latest news...")

# News fetching functions (optional use)
def fetch_ann_news():
    feed = feedparser.parse('https://www.animenewsnetwork.com/all/rss.xml')
    latest = feed.entries[0]
    return f"📢 ANN: {latest.title}\n{latest.link}"

def fetch_natalie_news():
    feed = feedparser.parse('https://natalie.mu/comic/feed/news')
    latest = feed.entries[0]
    return f"🗾 Natalie: {latest.title}\n{latest.link}"

async def fetch_crunchyroll_news():
    url = "https://www.crunchyroll.com/news"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html.parser')
            article = soup.find('a', class_='text-link')
            if article:
                title = article.text.strip()
                link = 'https://www.crunchyroll.com' + article['href']
                return f"🎬 Crunchyroll: {title}\n{link}"
            return "🎬 Crunchyroll: No news found."

# Add Telegram command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", get_news))

# --- FastAPI Routes ---
@app.post(f"/bot{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return {"status": "ok"}

# --- FastAPI Startup Event ---
@app.on_event("startup")
async def on_startup():
    # Initialize and start the Telegram bot application
    await application.initialize()
    await application.bot.set_webhook(url=f"{APP_URL}/bot{TOKEN}")
    await application.start()
    print(f"✅ Webhook set to {APP_URL}/bot{TOKEN}")

# --- FastAPI Shutdown Event (optional, for clean shutdown) ---
@app.on_event("shutdown")
async def on_shutdown():
    await application.stop()
    await application.shutdown()

# --- Main Entrypoint (only used for local testing) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("bot.main:app", host="0.0.0.0", port=port, reload=True)
