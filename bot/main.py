from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from fastapi import FastAPI, Request
import feedparser
import asyncio
import os
import uvicorn

# Load environment variables (Railway env vars)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("DOMAIN")
CHAT_ID = os.getenv("CHAT_ID")  # Chat ID required

app = FastAPI()
application = ApplicationBuilder().token(TOKEN).build()

# News sources (English only, anime/manga focused)
sources = [
    ("Crunchyroll", "https://cr-news-api-service.prd.crunchyrollsvc.com/v1/en-US/rss"),
]

# Store sent links to avoid reposting
sent_links = set()

# 🎯 /start Command
async def start(update: Update, context):
    await update.message.reply_text("👋 Welcome! Auto-news Bot is running!")

# 🎯 /news Command (Manual)
async def get_news(update: Update, context):
    await send_news()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", get_news))

# 📰 Fetch and Send News
async def send_news():
    for name, url in sources:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:  # Top 10 news
            title = entry.title
            link = entry.link
            # Only anime/manga related
            if not any(word in title.lower() for word in ["anime", "manga"]):
                continue
            if link in sent_links:
                continue  # Already sent

            sent_links.add(link)
            text = f"🌟 <b>New update from {name}!</b>\n\n📰 <b>{title}</b>\n🔗 {link}"
            await application.bot.send_message(
                chat_id=CHAT_ID,
                text=text,
                parse_mode="HTML"
            )
            await asyncio.sleep(2)  # Tiny pause between messages

# 🔄 Auto-post news every X seconds
async def auto_post_news():
    await application.bot.delete_webhook(drop_pending_updates=True)
    while True:
        await send_news()
        await asyncio.sleep(2 * 60 * 60)  # ⏰ Every 2 hours (adjust if needed)

# 📡 Webhook endpoint
@app.post(f"/bot{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return {"status": "ok"}

# 🛠 Main Function
def main():
    async def run():
        await application.bot.set_webhook(url=f"{APP_URL}/bot{TOKEN}")
        asyncio.create_task(auto_post_news())

    asyncio.run(run())

if __name__ == "__main__":
    main()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("bot.main:app", host="0.0.0.0", port=port)
