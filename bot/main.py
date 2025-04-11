from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
import feedparser
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("DOMAIN")  # Like "https://your-app.up.railway.app"

app = FastAPI()
application = ApplicationBuilder().token(TOKEN).build()

# Commands
async def start(update: Update, context):
    await update.message.reply_text("👋 Welcome! Send /news to get the latest anime/gaming news!")

async def news(update: Update, context):
    await update.message.reply_text("📰 Fetching top news...")

    # News sources (updated Crunchyroll)
    sources = [
        ("Crunchyroll", "https://cr-news-api-service.prd.crunchyrollsvc.com/v1/en-US/rss"),
        ("MyAnimeList", "https://myanimelist.net/rss/news.xml"),
        ("ANN", "https://www.animenewsnetwork.com/all/rss.xml"),
        ("Kotaku", "https://kotaku.com/rss"),
    ]

    for name, url in sources:
        feed = feedparser.parse(url)
        if not feed.entries:
            await update.message.reply_text(f"⚠️ No news found from {name}.")
            continue

        top_entries = feed.entries[:10]  # Get top 10

        for entry in top_entries:
            title = entry.title
            link = entry.link
            await update.message.reply_text(f"🗞️ {name}:\n<b>{title}</b>\n{link}", parse_mode="HTML")

# Setup handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", news))

# FastAPI webhook route
@app.post(f"/bot{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return {"status": "ok"}

def main():
    import asyncio

    async def run():
        await application.initialize()
        await application.bot.set_webhook(url=f"{APP_URL}/bot{TOKEN}")
        await application.start()
        print(f"Webhook set to {APP_URL}/bot{TOKEN}")

    asyncio.run(run())

if __name__ == "__main__":
    main()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("bot.main:app", host="0.0.0.0", port=port)
