# jikan_api.py

import aiohttp

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
    url = "https://api.jikan.moe/v4/news"
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
