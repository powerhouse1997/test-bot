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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # You need to set this in your .env!

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

            if anime_news and (not latest_news or anime_news[0]['link'] != latest_news[0]['link']):
                latest_news = anime_news
                await send_news_to_group(latest_news, category="Anime")

            if manga_news and (not latest_manga_news or manga_news[0]['link'] != latest_manga_news[0]['link']):
                latest_manga_news = manga_news
                await send_news_to_group(latest_manga_news, category="Manga")

        except Exception as e:
            logging.error(f"Error fetching news: {e}")

        await asyncio.sleep(600)  # 10 minutes

# Send news automatically to group
async def send_news_to_group(news_list, category="News"):
    if not news_list:
        return
    first_news = news_list[0]
    caption = (
        f"📰 <b>{category} News:</b> {first_news['title']}\n\n"
        f"📝 {first_news['summary'][:300]}...\n\n"
        f"🔗 <a href='{first_news['link']}'>Read Full</a>"
    )

    try:
        if first_news['thumbnail']:
            await bot.send_photo(
                chat_id=GROUP_CHAT_ID,
                photo=first_news['thumbnail'],
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

# Commands
async def latest_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not latest_news:
        await update.message.reply_text("No anime news available yet. Please try again later.")
        return
    await send_news_list(update, latest_news, "Anime")

async def latest_manga_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not latest_manga_news:
        await update.message.reply_text("No manga news available yet. Please try again later.")
        return
    await send_news_list(update, latest_manga_news, "Manga")

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not latest_news and not latest_manga_news:
        await update.message.reply_text("No news available yet. Please try again later.")
        return

    if update.effective_chat.id != int(GROUP_CHAT_ID):
        await update.message.reply_text("This command can only be used in the group!")
        return

    await send_news_to_group(latest_news, category="Anime")
    await send_news_to_group(latest_manga_news, category="Manga")
    await update.message.reply_text("Latest news sent to the group!")

# Helper: Send news list
async def send_news_list(update, news_list, category="News"):
    for news in news_list:
        caption = (
            f"📰 <b>{category} News:</b> {news['title']}\n\n"
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

# FastAPI startup event
@app.on_event("startup")
async def on_startup():
    await bot_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}")
    asyncio.create_task(fetch_latest_news())

# FastAPI route to receive Telegram updates
@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != BOT_TOKEN:
        return {"status": "invalid token"}

    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}

# FastAPI root route
@app.get("/")
def read_root():
    return {"message": "Bot is running!"}