from telegram.ext import ApplicationBuilder, CommandHandler
import feedparser
import aiohttp
from bs4 import BeautifulSoup
import os

# Load your .env (optional if you use Railway variables directly)
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("DOMAIN")  # Like "https://your-app.up.railway.app"

# News fetching functions
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

# Command handlers
async def start(update, context):
    await update.message.reply_text('Hello! Send /news to get the latest anime news.')

async def get_news(update, context):
    ann = fetch_ann_news()
    natalie = fetch_natalie_news()
    crunchy = await fetch_crunchyroll_news()

    news_message = f"{ann}\n\n{natalie}\n\n{crunchy}"
    await update.message.reply_text(news_message)

# Main Bot
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", get_news))

    # 🔥 Running webhook
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get('PORT', 8443)),
        webhook_url=f"{APP_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
