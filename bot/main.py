from fastapi import FastAPI, Request
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import aiohttp
import os
import uvicorn
import asyncio

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("DOMAIN")  # Railway ENV
CHAT_ID = os.getenv("CHAT_ID")  # Save your chat ID in Railway ENV
POST_INTERVAL = 2 * 60 * 60  # 2 hours in seconds

app = FastAPI()
application = ApplicationBuilder().token(TOKEN).build()

last_posted_titles = set()

# 🔥 Fetch news from Crunchyroll RSS
async def fetch_crunchyroll_news():
    url = "https://cr-news-api-service.prd.crunchyrollsvc.com/v1/en-US/rss"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()
            from xml.etree import ElementTree as ET
            root = ET.fromstring(text)
            items = root.findall('.//item')
            news = []
            for item in items[:10]:  # Top 10
                title = item.find('title').text
                link = item.find('link').text
                thumbnail = None
                # Try to get image from enclosure tag
                enclosure = item.find('enclosure')
                if enclosure is not None:
                    thumbnail = enclosure.attrib.get('url')

                if any(word in title.lower() for word in ["anime", "manga"]):
                    news.append((title, link, thumbnail))
            return news

# 🎯 Send news to a chat
async def send_news(update: Update = None, context: ContextTypes.DEFAULT_TYPE = None):
    global last_posted_titles
    news = await fetch_crunchyroll_news()
    new_news = [n for n in news if n[0] not in last_posted_titles]

    if not new_news:
        if update:
            await update.message.reply_text("🛑 No new anime/manga updates.")
        return

    for title, link, thumbnail in new_news:
        caption = f"🆕 *{title}*"
        button = InlineKeyboardButton("📖 Read Full Article", url=link)
        keyboard = InlineKeyboardMarkup([[button]])

        if update:
            if thumbnail:
                await update.message.reply_photo(photo=thumbnail, caption=caption, parse_mode="Markdown", reply_markup=keyboard)
            else:
                await update.message.reply_text(caption, parse_mode="Markdown", reply_markup=keyboard)
        else:
            if thumbnail:
                await application.bot.send_photo(chat_id=CHAT_ID, photo=thumbnail, caption=caption, parse_mode="Markdown", reply_markup=keyboard)
            else:
                await application.bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="Markdown", reply_markup=keyboard)

        last_posted_titles.add(title)

# 🎛 Keyboard
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📰 Get News Now"], ["ℹ️ Help"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Welcome! Please choose an option:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📰 Get News Now":
        await send_news(update, context)
    elif text == "ℹ️ Help":
        await update.message.reply_text(
            "ℹ️ *Crunchyroll News Bot*\n\n"
            "📰 Get the latest *anime* and *manga* news.\n"
            "⏰ Auto-posts every 2 hours.\n"
            "📖 Click '📰 Get News Now' anytime for fresh updates!",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❓ Please use the buttons below!")

# ⏰ Auto Post Task
async def auto_post():
    while True:
        await send_news()
        await asyncio.sleep(POST_INTERVAL)

@app.post(f"/bot{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return {"status": "ok"}

def main():
    async def run():
        await application.bot.set_webhook(url=f"{APP_URL}/bot{TOKEN}")
        print(f"Webhook set: {APP_URL}/bot{TOKEN}")
        asyncio.create_task(auto_post())

    asyncio.run(run())

if __name__ == "__main__":
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    main()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)