import asyncio
import feedparser
import logging
import os
import requests
from fastapi import FastAPI
from telegram import Update, Bot, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("CHAT_ID")

app = FastAPI()

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

# Auto fetch news
async def fetch_latest_news():
    global latest_news, latest_manga_news
    while True:
        anime_news = fetch_rss("https://www.animenewsnetwork.com/all/rss.xml")
        manga_news = fetch_rss("https://myanimelist.net/rss/news.xml")

        # Check if new news arrived
        if anime_news and (not latest_news or anime_news[0]['link'] != latest_news[0]['link']):
            latest_news = anime_news
            await send_news_to_group(latest_news, category="Anime")

        if manga_news and (not latest_manga_news or manga_news[0]['link'] != latest_manga_news[0]['link']):
            latest_manga_news = manga_news
            await send_news_to_group(latest_manga_news, category="Manga")

        await asyncio.sleep(600)  # Wait 10 minutes

# Send news to group automatically
async def send_news_to_group(news_list, category="News"):
    if not news_list:
        return
    first_news = news_list[0]
    caption = f"📰 <b>{category} News:</b> {first_news['title']}\n\n📝 {first_news['summary'][:300]}...\n\n🔗 <a href='{first_news['link']}'>Read Full</a>"

    try:
        if first_news['thumbnail']:
            await bot.send_photo(chat_id=GROUP_CHAT_ID, photo=first_news['thumbnail'], caption=caption, parse_mode="HTML")
        else:
            await bot.send_message(chat_id=GROUP_CHAT_ID, text=caption, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error sending news: {e}")

# User command: /latestnews
async def latest_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not latest_news:
        await update.message.reply_text("No anime news available yet. Please try again later.")
        return
    await send_news_list(update, latest_news, "Anime")

# User command: /latestmanga
async def latest_manga_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not latest_manga_news:
        await update.message.reply_text("No manga news available yet. Please try again later.")
        return
    await send_news_list(update, latest_manga_news, "Manga")

# Send news to user
async def send_news_list(update, news_list, category="News"):
    for news in news_list:
        caption = f"📰 <b>{category} News:</b> {news['title']}\n\n📝 {news['summary'][:300]}...\n\n🔗 <a href='{news['link']}'>Read Full</a>"
        try:
            if news['thumbnail']:
                await update.message.reply_photo(photo=news['thumbnail'], caption=caption, parse_mode="HTML")
            else:
                await update.message.reply_text(text=caption, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Error sending news: {e}")

# Telegram bot setup
bot_app.add_handler(CommandHandler("latestnews", latest_news_command))
bot_app.add_handler(CommandHandler("latestmanga", latest_manga_command))

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(fetch_latest_news())
    asyncio.create_task(bot_app.start())

@app.get("/")
def read_root():
    return {"message": "Bot is running!"}