import feedparser
import aiohttp
from bs4 import BeautifulSoup
from telegram.ext import ApplicationBuilder, CommandHandler
import asyncio
import os

# Bot token
TOKEN = os.getenv("BOT_TOKEN") or "your-bot-token-here"

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

# --- Telegram command handlers ---

async def start(update, context):
    await update.message.reply_text('Hello! I will send you the latest Anime News. Type /news to get news!')

async def get_news(update, context):
    ann = fetch_ann_news()
    natalie = fetch_natalie_news()
    crunchy = await fetch_crunchyroll_news()
    news_message = f"{ann}\n\n{natalie}\n\n{crunchy}"
    await update.message.reply_text(news_message)

# --- Main ---

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", get_news))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
