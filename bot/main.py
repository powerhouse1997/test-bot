import os
import feedparser
import aiohttp
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Set this in Railway Environment Variables
WEBHOOK_URL = os.getenv("DOMAIN")  # Your Railway public URL like https://your-bot.up.railway.app

# --- Fetch news functions ---

def fetch_ann_news():
    feed = feedparser.parse('https://www.animenewsnetwork.com/all/rss.xml')
    latest = feed.entries[0]
    return f"📢 ANN: {latest.title}\n{latest.link}"

def fetch_natalie_news():
    feed = feedparser.parse('https://natalie.mu/comic/feed/news')
    latest = feed.entries[0]
    return f"🗾 Natalie: {latest.title}\n{latest.link}"

async def fetch_crunchyroll_news():
    url = "https://www.crunchyroll.com/news"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html.parser')
            article = soup.find('a', class_='text-link')
            if article:
                title = article.text.strip()
                link = 'https://www.crunchyroll.com' + article['href']
                return f"🎬 Crunchyroll: {title}\n{link}"
            return "🎬 Crunchyroll: No news found."

def fetch_myanimelist_news():
    feed = feedparser.parse('https://myanimelist.net/rss/news.xml')
    latest = feed.entries[0]
    return f"🌟 MAL: {latest.title}\n{latest.link}"

def fetch_animeuk_news():
    feed = feedparser.parse('https://animeuknews.net/category/news/feed/')
    latest = feed.entries[0]
    return f"🇬🇧 AnimeUKNews: {latest.title}\n{latest.link}"

def fetch_otakuusa_news():
    feed = feedparser.parse('https://otakuusamagazine.com/feed/')
    latest = feed.entries[0]
    return f"🇺🇸 Otaku USA: {latest.title}\n{latest.link}"

# --- Telegram command handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! 📰 I will send you the latest Anime News. Type /news to get updates!')

async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ann = fetch_ann_news()
    natalie = fetch_natalie_news()
    crunchy = await fetch_crunchyroll_news()
    mal = fetch_myanimelist_news()
    animeuk = fetch_animeuk_news()
    otakuusa = fetch_otakuusa_news()
    news_message = f"{ann}\n\n{natalie}\n\n{crunchy}\n\n{mal}\n\n{animeuk}\n\n{otakuusa}"
    await update.message.reply_text(news_message)

# --- Main function ---

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", get_news))

    print("Bot is running with Webhook...")

    # Start the bot
    await app.start()
    await app.bot.set_webhook(url=DOMAIN)

    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=WEBHOOK_URL,
    )

    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
