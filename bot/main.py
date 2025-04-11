import asyncio
import feedparser
import logging
import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
DOMAIN = os.getenv("DOMAIN")

# Initialize FastAPI app
app = FastAPI()

# Initialize Telegram bot
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
bot = Bot(BOT_TOKEN)

latest_news = []
latest_manga_news = []

# Fetch RSS feed
def fetch_rss(url):
    feed = feedparser.parse(url)
    entries = []
    for entry in feed.entries[:5]:  # Latest 5 news
        thumbnail = ""
        if "media_thumbnail" in entry:
            thumbnail = entry.media_thumbnail[0]['url']
        elif "media_content" in entry:
            thumbnail = entry.media_content[0]['url']
        entries.append({
            'title': entry.title,
            'link': entry.link,
            'summary': entry.summary,
            'thumbnail': thumbnail,
            'published': entry.get("published", "Unknown date")
        })
    return entries

# Auto fetch latest news
async def fetch_latest_news():
    global latest_news, latest_manga_news
    while True:
        try:
            anime_news = fetch_rss("https://www.animenewsnetwork.com/all/rss.xml")
            manga_news = fetch_rss("https://myanimelist.net/rss/news.xml")

            if anime_news and (not latest_news or anime_news[0]['link'] != latest_news[0]['link']):
                latest_news = anime_news
                await send_bulk_news(latest_news, category="Anime")

            if manga_news and (not latest_manga_news or manga_news[0]['link'] != latest_manga_news[0]['link']):
                latest_manga_news = manga_news
                await send_bulk_news(latest_manga_news, category="Manga")

        except Exception as e:
            logging.error(f"Error fetching news: {e}")

        await asyncio.sleep(600)  # 10 minutes

# Send multiple news with flood control
async def send_bulk_news(news_list, category="News"):
    if not news_list:
        return

    for news in news_list:
        caption = (
            f"📰 <b>{category} News:</b> {news['title']}\n"
            f"🗓 <b>Published:</b> {news['published']}\n\n"
            f"📝 {news['summary'][:300]}...\n\n"
            f"🔗 <a href='{news['link']}'>Read Full</a>"
        )

        try:
            if news['thumbnail']:
                await bot.send_photo(
                    chat_id=GROUP_CHAT_ID,
                    photo=news['thumbnail'],
                    caption=caption,
                    parse_mode="HTML"
                )
            else:
                await bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=caption,
                    parse_mode="HTML"
                )
            await asyncio.sleep(1.5)  # Delay to avoid flood control
        except Exception as e:
            logging.error(f"Error sending news: {e}")
            await asyncio.sleep(30)  # If flood, wait longer

# Command: /latestnews
async def latest_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not latest_news:
        await update.message.reply_text("No anime news available yet. Please try again later.")
        return
    await send_news_list(update, latest_news, "Anime")

# Command: /latestmanga
async def latest_manga_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not latest_manga_news:
        await update.message.reply_text("No manga news available yet. Please try again later.")
        return
    await send_news_list(update, latest_manga_news, "Manga")

# Command: /news
async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != int(GROUP_CHAT_ID):
        await update.message.reply_text("This command can only be used in the group!")
        return
    await send_bulk_news(latest_news, category="Anime")
    await send_bulk_news(latest_manga_news, category="Manga")
    await update.message.reply_text("All today's news sent!")

# Command: /anime
async def anime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_bulk_news(latest_news, category="Anime")

# Command: /manga
async def manga_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_bulk_news(latest_manga_news, category="Manga")

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Available Commands:\n\n"
        "/latestnews - Latest Anime News\n"
        "/latestmanga - Latest Manga News\n"
        "/news - Send today's Anime and Manga news\n"
        "/anime - Only today's Anime news\n"
        "/manga - Only today's Manga news\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text)

# Helper: Send news list to user
async def send_news_list(update, news_list, category="News"):
    for news in news_list:
        caption = (
            f"📰 <b>{category} News:</b> {news['title']}\n"
            f"🗓 <b>Published:</b> {news['published']}\n\n"
            f"📝 {news['summary'][:300]}...\n\n"
            f"🔗 <a href='{news['link']}'>Read Full</a>"
        )
        try:
            if news['thumbnail']:
                await update.message.reply_photo(
                    photo=news['thumbnail'],
                    caption=caption,
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    text=caption,
                    parse_mode="HTML"
                )
            await asyncio.sleep(1.5)
        except Exception as e:
            logging.error(f"Error sending user news: {e}")
            await asyncio.sleep(30)

# Register bot commands
bot_app.add_handler(CommandHandler("latestnews", latest_news_command))
bot_app.add_handler(CommandHandler("latestmanga", latest_manga_command))
bot_app.add_handler(CommandHandler("news", news_command))
bot_app.add_handler(CommandHandler("anime", anime_command))
bot_app.add_handler(CommandHandler("manga", manga_command))
bot_app.add_handler(CommandHandler("help", help_command))

# Startup event
@app.on_event("startup")
async def on_startup():
    webhook_url = f"{DOMAIN}/webhook"
    await bot_app.bot.set_webhook(webhook_url)
    asyncio.create_task(fetch_latest_news())

# Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    await bot_app.update_queue.put(Update.de_json(update, bot_app.bot))
    return {"ok": True}

# FastAPI root
@app.get("/")
def read_root():
    return {"message": "Bot is running!"}