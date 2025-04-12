import aiohttp

BASE_URL = "https://api.jikan.moe/v4"

async def search_jikan(type_: str, query: str):
    url = f"{BASE_URL}/{type_}"
    params = {"q": query, "limit": 1}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                print(f"Error fetching data from Jikan: HTTP {resp.status}")
                return []
            data = await resp.json()
            return data.get("data", [])

async def get_top_anime():
    url = f"{BASE_URL}/top/anime"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Error fetching top anime: HTTP {resp.status}")
                return []
            data = await resp.json()
            return data.get("data", [])

async def get_current_season():
    url = f"{BASE_URL}/seasons/now"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Error fetching current season: HTTP {resp.status}")
                return []
            data = await resp.json()
            return data.get("data", [])
