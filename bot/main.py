from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
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

# Fetch Crunchyroll News
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
                news_list.append(f"🎬 {title}\n{link}")
            return news_list

# Telegram Command Handlers
async def start(update: Update, context):
    await update.message.reply_text("👋 Welcome! Bot is working.")

async def get_news(update: Update, context):
    await update.message.reply_text("📰 Fetching Top 10 Crunchyroll news...")

    news_list = await fetch_crunchyroll_news()

    for news_item in news_list:
        await update.message.reply_text(news_item)

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
