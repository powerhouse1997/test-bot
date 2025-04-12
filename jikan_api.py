# jikan_api.py

import aiohttp
import feedparser
import re
from jikan_api import fetch_anime_news  # Assuming the function is in jikan_api.py

# Define the fetch_season_now function here.
async def fetch_season_now():
    url = "https://api.jikan.moe/v4/seasons/now"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["data"]
                else:
                    return None
        except Exception as e:
            return None

# Define the search_jikan function for the anime search, if necessary.
async def search_jikan(type: str, query: str):
    url = f"https://api.jikan.moe/v4/{type}?q={query}&limit=1"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["data"]
                else:
                    return []
        except Exception as e:
            return []


async def fetch_anime_news():
    url = "https://www.animenewsnetwork.com/all/rss.xml"
    feed = feedparser.parse(url)

    news_items = []
    for entry in feed.entries[:5]:  # Fetch top 5 news
        # Try to extract image from description
        description = entry.get("description", "")
        img_match = re.search(r'<img[^>]+src="([^"]+)"', description)
        image_url = img_match.group(1) if img_match else None

        news_items.append({
            "title": entry.title,
            "url": entry.link,
            "published_at": entry.published,
            "thumbnail": image_url
        })

    return news_items
