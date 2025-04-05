import httpx
import anthropic
from deep_translator import GoogleTranslator
import dateparser
import os

anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

async def get_weather(city):
    # Dummy weather info
    return f"The weather in {city} is 25°C, clear sky ☀️"

async def translate_text(text, lang):
    translated = GoogleTranslator(target=lang).translate(text)
    return translated

async def parse_reminder_time(text):
    dt = dateparser.parse(text, settings={"PREFER_DATES_FROM": "future"})
    return dt
