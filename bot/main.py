import feedparser
import aiohttp
from bs4 import BeautifulSoup
from telegram.ext import ApplicationBuilder, CommandHandler
import asyncio
import os

# Bot token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "your-bot-token-here"

# --- Fetch news functions ---

def fetch_ann_news():
    feed = feedparser.parse('https://www.animenewsnetwork.com/all/rss.xml')
    latest = feed.entries[0]
    return f"📢 ANN: {latest.title}\n{latest.link}"
   
def fetch_animeuk_news():
    feed = feedparser.parse('https://animeuknews.net/feed/')
    latest = feed.entries[0]
    return f"🇬🇧 AnimeUK: {latest.title}\n{latest.link}"


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
def fetch_mal_news():
    feed = feedparser.parse('https://myanimelist.net/rss/news.xml')
    latest = feed.entries[0]
    return f"🐉 MAL: {latest.title}\n{latest.link}"


# --- Telegram command handlers ---

async def start(update, context):
    await update.message.reply_text('Hello! I will send you the latest Anime News. Type /news to get news!')

async def get_news(update, context):
    ann = fetch_ann_news()
    crunchy = await fetch_crunchyroll_news()
    mal = fetch_mal_news()
    animeuk = fetch_animeuk_news()

    news_message = f"{ann}\n\n{crunchy}\n\n{mal}\n\n{animeuk}\n\n{otakuusa}"
    await update.message.reply_text(news_message)


# --- Main ---

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("news", get_news))

print("Bot is running with Webhook...")

await app.start()
await app.bot.set_webhook("https://your-railway-app.up.railway.app/")  # <--- your public URL
await app.updater.start_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get('PORT', 8443)),
    url_path="",
    webhook_url="https://your-railway-app.up.railway.app/",
)
await app.updater.idle()
