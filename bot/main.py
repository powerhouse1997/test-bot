from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
import feedparser
import os
from fastapi import FastAPI, Request
import uvicorn

# No need for load_dotenv()

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
APP_URL = os.environ["DOMAIN"]  # Example: https://your-app.up.railway.app

# Initialize FastAPI and Telegram Application
app = FastAPI()
application = ApplicationBuilder().token(TOKEN).build()

# Telegram Bot Commands
async def start(update: Update, context):
    await update.message.reply_text("👋 Welcome! Send /news to get the latest news!")

async def news(update: Update, context):
    await update.message.reply_text("📰 Fetching top news...")

    sources = [
        ("Crunchyroll", "https://cr-news-api-service.prd.crunchyrollsvc.com/v1/en-US/rss"),
        ("MyAnimeList", "https://myanimelist.net/rss/news.xml"),
        ("Anime News Network", "https://www.animenewsnetwork.com/all/rss.xml"),
        ("Kotaku", "https://kotaku.com/rss"),
    ]

    for name, url in sources:
        feed = feedparser.parse(url)
        if not feed.entries:
            await update.message.reply_text(f"⚠️ No news found from {name}.")
            continue

        for entry in feed.entries[:10]:  # Top 10
            title = entry.title
            link = entry.link
            await update.message.reply_text(f"🗞️ <b>{name}</b>\n<b>{title}</b>\n{link}", parse_mode="HTML")

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", news))

# FastAPI Webhook route
@app.post(f"/bot{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return {"status": "ok"}

async def set_webhook():
    """Set the webhook on startup."""
    await application.bot.set_webhook(url=f"{APP_URL}/bot{TOKEN}")
    print(f"✅ Webhook set to {APP_URL}/bot{TOKEN}")

@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await set_webhook()
    await application.start()

@app.on_event("shutdown")
async def on_shutdown():
    await application.stop()
    await application.shutdown()

# Main
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("bot.main:app", host="0.0.0.0", port=port)
