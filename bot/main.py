import asyncio
import feedparser
import logging
import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dateutil import parser
import pytz

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
DOMAIN = os.getenv("DOMAIN")  # Webhook domain

# Initialize FastAPI app
app = FastAPI()

# Initialize Telegram bot
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
bot = Bot(BOT_TOKEN)

latest_news = []
latest_manga_news = []

# Set your local timezone
local_timezone = pytz.timezone("Asia/Kolkata")

# Fetch RSS feed
def fetch_rss(url):
    feed = feedparser.parse(url)
    entries = []
    for entry in feed.entries[:10]:  # Fetch latest 10 news
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
            'published': entry.published
        })
    return entries

# Auto fetch latest news
async def fetch_latest_news():
    global latest_news, latest_manga_news
    while True:
        try:
            anime_news = fetch_rss("https://www.animenewsnetwork.com/all/rss.xml")
            manga_news = fetch_rss("https://myanimelist.net/rss/news.xml")

            # Check and send new anime news
            if anime_news:
                if not latest_news or anime_news[0]['link'] != latest_news[0]['link']:
                    new_items = [news for news in anime_news if news['link'] not in [n['link'] for n in latest_news]]
                    latest_news = anime_news
                    for news in new_items:
                        await send_single_news_to_group(news, category="Anime")

            # Check and send new manga news
            if manga_news:
                if not latest_manga_news or manga_news[0]['link'] != latest_manga_news[0]['link']:
                    new_items = [news for news in manga_news if news['link'] not in [n['link'] for n in latest_manga_news]]
                    latest_manga_news = manga_news
                    for news in new_items:
                        await send_single_news_to_group(news, category="Manga")

        except Exception as e:
            logging.error(f"Error fetching news: {e}")

        await asyncio.sleep(600)  # Wait 10 minutes

# Send one news automatically
async def send_single_news_to_group(news, category="News"):
    published_time = ""
    try:
        published_dt = parser.parse(news['published'])
        published_dt = published_dt.astimezone(local_timezone)
        published_time = published_dt.strftime("%d %b %Y, %I:%M %p")
    except Exception as e:
        logging.error(f"Error parsing published time: {e}")

    caption = (
        f"📰 <b>{category} News:</b> {news['title']}\n\n"
        f"🕒 <b>Published:</b> {published_time}\n\n"
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
    except Exception as e:
        logging.error(f"Error sending news: {e}")

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
    if not latest_news and not latest_manga_news:
        await update.message.reply_text("No news available yet. Please try again later.")
        return

    if update.effective_chat.id != int(GROUP_CHAT_ID):
        await update.message.reply_text("This command can only be used in the group!")
        return

    await update.message.reply_text("📰 <b>Today's Latest News</b>:", parse_mode="HTML")
    await send_news_list(update, latest_news, "Anime")
    await send_news_list(update, latest_manga_news, "Manga")

# Helper: Send multiple news
async def send_news_list(update, news_list, category="News"):
    max_news = 10  # Show maximum 10 news at once
    for news in news_list[:max_news]:
        published_time = ""
        try:
            published_dt = parser.parse(news['published'])
            published_dt = published_dt.astimezone(local_timezone)
            published_time = published_dt.strftime("%d %b %Y, %I:%M %p")
        except Exception as e:
            logging.error(f"Error parsing published time: {e}")

        caption = (
            f"📰 <b>{category} News:</b> {news['title']}\n\n"
            f"🕒 <b>Published:</b> {published_time}\n\n"
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
        except Exception as e:
            logging.error(f"Error sending user news: {e}")

# Register bot commands
bot_app.add_handler(CommandHandler("latestnews", latest_news_command))
bot_app.add_handler(CommandHandler("latestmanga", latest_manga_command))
bot_app.add_handler(CommandHandler("news", news_command))

# Startup event: Set webhook
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

# FastAPI root route
@app.get("/")
def read_root():
    return {"message": "Bot is running!"}