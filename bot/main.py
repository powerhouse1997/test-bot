import asyncio
import feedparser
import logging
import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp

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
latest_trending_anime = []

# Fetch RSS feed
def fetch_rss(url, limit=5):
    feed = feedparser.parse(url)
    entries = []
    for entry in feed.entries[:limit]:
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

# Fetch top trending anime
async def fetch_trending_anime():
    url = "https://api.jikan.moe/v4/top/anime?filter=airing"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            trending = []
            for anime in data.get("data", [])[:5]:
                trending.append({
                    'title': anime.get('title'),
                    'url': anime.get('url'),
                    'image': anime.get('images', {}).get('jpg', {}).get('large_image_url'),
                    'score': anime.get('score'),
                    'episodes': anime.get('episodes'),
                    'status': anime.get('status'),
                    'genres': [genre['name'] for genre in anime.get('genres', [])]
                })
            return trending

# Auto fetch latest news and trending
async def fetch_latest_news():
    global latest_news, latest_manga_news, latest_trending_anime
    while True:
        try:
            anime_news = fetch_rss("https://www.animenewsnetwork.com/all/rss.xml")
            manga_news = fetch_rss("https://myanimelist.net/rss/news.xml")
            trending = await fetch_trending_anime()

            if anime_news and (not latest_news or anime_news[0]['link'] != latest_news[0]['link']):
                latest_news = anime_news
                await send_news_to_group(latest_news, category="Anime")

            if manga_news and (not latest_manga_news or manga_news[0]['link'] != latest_manga_news[0]['link']):
                latest_manga_news = manga_news
                await send_news_to_group(latest_manga_news, category="Manga")

            if trending and (not latest_trending_anime or trending[0]['title'] != latest_trending_anime[0]['title']):
                latest_trending_anime = trending
                await send_trending_to_group(latest_trending_anime)

        except Exception as e:
            logging.error(f"Error fetching news: {e}")

        await asyncio.sleep(600)  # Fetch every 10 minutes

# Send news automatically
async def send_news_to_group(news_list, category="News"):
    if not news_list:
        return
    first_news = news_list[0]
    caption = (
        f"✨ <b>{category} News Update!</b>\n\n"
        f"🏷️ <b>Title:</b> {first_news['title']}\n"
        f"🗓️ <b>Published:</b> {first_news['published']}\n\n"
        f"📝 {first_news['summary'][:300]}...\n\n"
        f"🔗 <a href='{first_news['link']}'>Read More</a>\n\n"
        f"#AnimeNews #MangaNews #OtakuWorld"
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

# Send trending anime
async def send_trending_to_group(trending_list):
    for anime in trending_list:
        genres = ', '.join(anime['genres']) if anime['genres'] else 'N/A'
        caption = (
            f"🔥 <b>Top Trending Anime</b> 🔥\n\n"
            f"🏷️ <b>Title:</b> {anime['title']}\n"
            f"⭐ <b>Rating:</b> {anime['score']}\n"
            f"🎬 <b>Episodes:</b> {anime['episodes']}\n"
            f"📡 <b>Status:</b> {anime['status']}\n"
            f"🎭 <b>Genres:</b> {genres}\n\n"
            f"🔗 <a href='{anime['url']}'>View on MyAnimeList</a>\n\n"
            f"#TrendingAnime #NowAiring #AnimeWorld"
        )

        try:
            if anime['image']:
                await bot.send_photo(
                    chat_id=GROUP_CHAT_ID,
                    photo=anime['image'],
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
            logging.error(f"Error sending trending anime: {e}")

# Commands
async def latest_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not latest_news:
        await update.message.reply_text("No anime news available yet. Please try again later.")
        return
    await send_all_news(update, latest_news, "Anime")

async def latest_manga_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not latest_manga_news:
        await update.message.reply_text("No manga news available yet. Please try again later.")
        return
    await send_all_news(update, latest_manga_news, "Manga")

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != int(GROUP_CHAT_ID):
        await update.message.reply_text("This command can only be used in the group!")
        return

    await send_news_to_group(latest_news, category="Anime")
    await send_news_to_group(latest_manga_news, category="Manga")
    await send_trending_to_group(latest_trending_anime)
    await update.message.reply_text("🚀 All latest news and trending anime sent!")

# Helper: Send all news
async def send_all_news(update, news_list, category="News"):
    for news in news_list:
        caption = (
            f"📰 <b>{category} News:</b> {news['title']}\n\n"
            f"🗓️ <b>Published:</b> {news['published']}\n"
            f"📝 {news['summary'][:300]}...\n\n"
            f"🔗 <a href='{news['link']}'>Read Full</a>\n\n"
            f"#AnimeUpdates #MangaBuzz"
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
    return {"message": "Legendary Anime Bot is Running!"}