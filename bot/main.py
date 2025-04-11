import asyncio
import feedparser
import logging
import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dateutil import parser, tz

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

# Set local timezone
local_timezone = tz.tzlocal()

# Global news storage
latest_anime_news = []
latest_manga_news = []
sent_news_links = set()

# --- Helper function to safely send messages ---
async def safe_send(bot_method, *args, **kwargs):
    while True:
        try:
            return await bot_method(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if "retry after" in error_msg:
                import re
                wait_seconds = 30
                match = re.search(r"retry after (\d+)", error_msg)
                if match:
                    wait_seconds = int(match.group(1))
                logging.warning(f"Flood control hit! Waiting {wait_seconds} seconds.")
                await asyncio.sleep(wait_seconds + 1)
            else:
                logging.error(f"Error in safe_send: {e}")
                return None

# --- Fetch RSS feed ---
def fetch_rss(url):
    feed = feedparser.parse(url)
    entries = []
    for entry in feed.entries[:10]:  # Latest 10 news
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

# --- Fetch latest news every 10 minutes ---
async def fetch_latest_news():
    global latest_anime_news, latest_manga_news
    while True:
        try:
            anime_news = fetch_rss("https://www.animenewsnetwork.com/all/rss.xml")
            manga_news = fetch_rss("https://myanimelist.net/rss/news.xml")

            # Check for new anime news
            for news in anime_news:
                if news['link'] not in sent_news_links:
                    await send_news_to_group(news, "Anime")
                    sent_news_links.add(news['link'])

            # Check for new manga news
            for news in manga_news:
                if news['link'] not in sent_news_links:
                    await send_news_to_group(news, "Manga")
                    sent_news_links.add(news['link'])

            latest_anime_news = anime_news
            latest_manga_news = manga_news

        except Exception as e:
            logging.error(f"Error fetching news: {e}")

        await asyncio.sleep(600)  # wait 10 minutes

# --- Send single news to group ---
async def send_news_to_group(news, category="News"):
    if not news:
        return

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
            await safe_send(bot.send_photo,
                chat_id=GROUP_CHAT_ID,
                photo=news['thumbnail'],
                caption=caption,
                parse_mode="HTML"
            )
        else:
            await safe_send(bot.send_message,
                chat_id=GROUP_CHAT_ID,
                text=caption,
                parse_mode="HTML"
            )
    except Exception as e:
        logging.error(f"Error sending news: {e}")

# --- /latestnews command ---
async def latest_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not latest_anime_news:
        await update.message.reply_text("No anime news available yet. Please try again later.")
        return
    await send_news_list(update, latest_anime_news, "Anime")

# --- /latestmanga command ---
async def latest_manga_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not latest_manga_news:
        await update.message.reply_text("No manga news available yet. Please try again later.")
        return
    await send_news_list(update, latest_manga_news, "Manga")

# --- /news command ---
async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != int(GROUP_CHAT_ID):
        await update.message.reply_text("This command can only be used in the group!")
        return

    if not latest_anime_news and not latest_manga_news:
        await update.message.reply_text("No news available yet. Please try again later.")
        return

    await send_news_list(update, latest_anime_news, "Anime")
    await send_news_list(update, latest_manga_news, "Manga")
    await update.message.reply_text("All today's news sent to the group!")

# --- Send full news list ---
async def send_news_list(update, news_list, category="News"):
    max_news = 10
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
                await safe_send(update.message.reply_photo,
                    photo=news['thumbnail'],
                    caption=caption,
                    parse_mode="HTML"
                )
            else:
                await safe_send(update.message.reply_text,
                    text=caption,
                    parse_mode="HTML"
                )
        except Exception as e:
            logging.error(f"Error sending user news: {e}")

        await asyncio.sleep(2)  # short pause to avoid flood

# --- Register bot commands ---
bot_app.add_handler(CommandHandler("latestnews", latest_news_command))
bot_app.add_handler(CommandHandler("latestmanga", latest_manga_command))
bot_app.add_handler(CommandHandler("news", news_command))

# --- On bot startup ---
@app.on_event("startup")
async def on_startup():
    webhook_url = f"{DOMAIN}/webhook"
    await bot_app.bot.set_webhook(webhook_url)
    asyncio.create_task(fetch_latest_news())

# --- Webhook endpoint ---
@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    await bot_app.update_queue.put(Update.de_json(update, bot_app.bot))
    return {"ok": True}

# --- Root route ---
@app.get("/")
def read_root():
    return {"message": "Bot is running!"}