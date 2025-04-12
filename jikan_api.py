from jikanpy import Jikan

# Initialize Jikan object
jikan = Jikan()

async def search_jikan(endpoint, query, limit=1):
    try:
        if endpoint == 'anime':
            return jikan.search('anime', query, page=1)['results'][:limit]
        elif endpoint == 'manga':
            return jikan.search('manga', query, page=1)['results'][:limit]
        elif endpoint == 'characters':
            return jikan.search('characters', query, page=1)['results'][:limit]
        elif endpoint == 'season':
            return jikan.season()  # For current season
        elif endpoint == 'top':
            return jikan.top('anime')  # Default top anime
        return []
    except Exception as e:
        print(f"Error fetching data from Jikan: {e}")
        return []

# Fetching anime news
async def fetch_anime_news():
    try:
        news = jikan.news()  # Using jikanpy to fetch news
        return news[:5]  # Get top 5 news items
    except Exception as e:
        print(f"Error fetching anime news: {e}")
        return []
        
async def fetch_season_now():
    try:
        return jikan.season()['anime']
    except Exception as e:
        print(f"Error fetching current season: {e}")
        return []
