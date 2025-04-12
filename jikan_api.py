import aiohttp
import logging
from config import JIKAN_API_URL

async def fetch_json(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logging.error(f"Failed to fetch {url}: Status {response.status}")
    except Exception as e:
        logging.error(f"Exception while fetching {url}: {e}")
    return None

async def search_jikan(endpoint, query, limit=1):
    from urllib.parse import quote
    url = f"{JIKAN_API_URL}/{endpoint}?q={quote(query)}&limit={limit}"
    data = await fetch_json(url)
    return data.get("data", []) if data else []
