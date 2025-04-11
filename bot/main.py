from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
import feedparser
import aiohttp
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("DOMAIN")

app = FastAPI()
application = ApplicationBuilder().token(TOKEN).build()

# ----- News Functions -----

async def fetch_crunchyroll_news():
    url = "https://www.crunchyroll.com/news"
    news_list = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.find_all('a', class_='text-link', limit=10)
            for article in articles:
                title = article.text.strip()
                link = 'https://www.crunchyroll.com' + article['href']
                news_list.append(f"🎥 [Crunchyroll] {title}\n{link}")
    return news_list


def fetch_myanimelist_news():
    feed = feedparser.parse('https://myanimelist.net/rss/news.xml')
    news_list = []
    for entry in feed.entries[:10]:
        title = entry.title
        link = entry.link
        news_list.append(f"🖊️ [MyAnimeList] {title}\n{link}")
    return news_list


def fetch_ann_news():
    feed = feedparser.parse('https://www.animenewsnetwork.com/all/rss.xml')
    news_list = []
    for entry in feed.entries[:10]:
        title = entry.title
        link = entry.link
        news_list.append(f"📢 [ANN] {title}\n{link}")
    return news_list


def fetch_kotaku_news():
    feed = feedparser.parse('https://kotaku.com/tag/anime/rss')
    news_list = []
    for entry in feed.entries[:10]:
        title = entry.title
        link = entry.link
        news_list.append(f"🕵️ [Kotaku] {title}\n{link}")
    return news_list


# ----- Commands -----

async def start(update: Update, context):
    await update.message.reply_text("\ud83d\udc4b Welcome! Use /news to get the latest anime news!")


async def get_news(update: Update, context):
    await update.message.reply_text("\ud83d\udcf0 Fetching top anime news...")

    cr_news = await fetch_crunchyroll_news()
    mal_news = fetch_myanimelist_news()
    ann_news = fetch_ann_news()
    kotaku_news = fetch_kotaku_news()

    all_news = cr_news + mal_news + ann_news + kotaku_news

    # Limit to 10 random news if needed
    for news_item in all_news[:10]:
        await update.message.reply_text(news_item)


# ----- Webhook Setup -----

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("news", get_news))

@app.post(f"/bot{TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return {"status": "ok"}


def main():
    import asyncio

    async def run():
        await application.bot.set_webhook(url=f"{APP_URL}/bot{TOKEN}")
        print(f"Webhook set to {APP_URL}/bot{TOKEN}")

    asyncio.run(run())

if __name__ == "__main__":
    main()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("bot.main:app", host="0.0.0.0", port=port)
