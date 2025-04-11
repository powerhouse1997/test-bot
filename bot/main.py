from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
import feedparser
import aiohttp
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn
import asyncio

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("DOMAIN")  # Example: "https://your-app.up.railway.app"

# Create FastAPI app
app = FastAPI()

# Create Telegram Application
application = ApplicationBuilder().token(TOKEN).build()

# News functions
def fetch_ann_news():
    feed = feedparser.parse('https://www.animenewsnetwork.com/all/rss.xml')
    news_items = feed.entries[:10]
    news_list = [f"📢 ANN: {item.title}\n{item.link}" for item in news_items]
    return "\n\n".join(news_list)

def fetch_natalie_news():
    feed = feedparser.parse('https://natalie.mu/comic/feed/news')
    news_items = feed.entries[:10]
    news_list = [f"🗾 Natalie: {item.title}\n{item.link}" for item in news_items]
    return "\n\n".join(news_list)

async def fetch_crunchyroll_news():
    url = "https://www.crunchyroll.com/news"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.find_all('a', class_='text-link', limit=10)
            news_list = []
            for article in articles:
                title = article.text.strip()
                link = 'https://www.crunchyroll.com' + article['href']
                news_list.append(f"🎬 Crunchyroll: {title}\n{link}")
            if news_list:
                return "\n\n".join(news_list)
            return "🎬 Crunchyroll: No news found."

# Telegram Command Handlers
async def start(update: Update, context):
    await update.message.reply_text("👋 Welcome! Bot is working.")

async def get_news(update: Update, context):
    loading_message = await update.message.reply_text("📰 Fetching Top 10 news...")

    ann_news = fetch_ann_news()
    natalie_news = fetch_natalie_news()
    crunchyroll_news = await fetch_crunchyroll_news()

    news_message = f"📰 Latest News Updates\n\n{ann_news}\n\n{natalie_news}\n\n{crunchyroll_news}"

    await loading_message.edit_text(news_message)

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", get_news))

# FastAPI route for webhook
@app.post(f"/bot{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return {"status": "ok"}

# Setup webhook when server starts
@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=f"{APP_URL}/bot{TOKEN}")
    print(f"Webhook set to {APP_URL}/bot{TOKEN}")

@app.on_event("shutdown")
async def on_shutdown():
    await application.stop()
    await application.shutdown()

# Entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("bot.main:app", host="0.0.0.0", port=port, reload=False)
