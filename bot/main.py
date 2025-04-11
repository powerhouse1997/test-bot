import asyncio
import feedparser
import logging
import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

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

# Sources
ANIME_SOURCES = [
    "https://www.animenewsnetwork.com/all/rss.xml",
    "https://www.crunchyroll.com/newsrss",
    "https://www.animenewsnetwork.com/news/rss.xml?category=anime",
    "https://www.animenewsnetwork.com/news/rss.xml?category=interest",
]

MANGA_SOURCES = [
    "https://myanimelist.net/rss/news.xml",
    "https://www.animenewsnetwork.com/news/rss.xml?category=manga",
]

# Fetch RSS feed
def fetch_rss(url):
    feed = feedparser.parse(url)
    entries = []
    for entry in feed.entries[:5]:  # Latest 5 news per feed
        thumbnail = ""
        if "media_content" in entry:
            thumbnail = entry.media_content[0]['url']
        elif "media_thumbnail" in entry:
            thumbnail = entry.media_thumbnail[0]['url']
        
        published = entry.get('published', '')
        if published:
            try:
                published = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M')
            except Exception:
                pass
        
        entries.append({
            'title': entry.title,
            'link': entry.link,
            'summary': entry.summary,
            'thumbnail': thumbnail,
            'published': published
        })
    return entries

# Auto fetch latest news
async def fetch_latest_news():
    global latest_news, latest_manga_news
    while True:
        try:
            anime_news = []
            for url in ANIME_SOURCES:
                anime_news.extend(fetch_rss(url))
            
            manga_news = []
            for url in MANGA_SOURCES:
                manga_news.extend(fetch_rss(url))

            # Remove duplicate news by link
            anime_news = {item['link']: item for item in anime_news}.values()
            manga_news = {item['link']: item for item in manga_news}.values()

            anime_news = sorted(anime_news, key=lambda x: x['published'], reverse=True)
            manga_news = sorted(manga_news, key=lambda x: x['published'], reverse=True)

            # Send only new news
            if anime_news and (not latest_news or list(anime_news)[0]['link'] != latest_news[0]['link']):
                new_anime_news = [n for n in anime_news if n['link'] != latest_news[0]['link']] if latest_news else list(anime_news)
                latest_news = list(anime_news)
                for news in new_anime_news:
                    await send_news_to_group(news, category="Anime")
                    await asyncio.sleep(1)  # Avoid flood control

            if manga_news and (not latest_manga_news or list(manga_news)[0]['link'] != latest_manga_news[0]['link']):
                new_manga_news = [n for n in manga_news if n['link'] != latest_manga_news[0]['link']] if latest_manga_news else list(manga_news)
                latest_manga_news = list(manga_news)
                for news in new_manga_news:
                    await send_news_to_group(news, category="Manga")
                    await asyncio.sleep(1)  # Avoid flood control

        except Exception as e:
            logging.error(f"Error fetching news: {e}")

        await asyncio.sleep(600)  # 10 minutes

# Send news automatically to group
async def send_news_to_group(news, category="News"):
    if not news:
        return
    
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

    for news in latest_news[:5]:
        await send_news_to_group(news, category="Anime")
        await asyncio.sleep(1)  # Sleep to avoid flood

    for news in latest_manga_news[:5]:
        await send_news_to_group(news, category="Manga")
        await asyncio.sleep(1)  # Sleep to avoid flood

    await update.message.reply_text("Latest anime and manga news sent to the group!")

# Helper: Send news list
async def send_news_list(update, news_list, category="News"):
    for news in news_list[:5]:  # Send only top 5
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
            await asyncio.sleep(1)  # Sleep to avoid flood
        except Exception as e:
            logging.error(f"Error sending user news: {e}")

# Register bot commands
bot_app.add_handler(CommandHandler("latestnews", latest_news_command))
bot_app.add_handler(CommandHandler("latestmanga", latest_manga_command))
bot_app.add_handler(CommandHandler("news", news_command))

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