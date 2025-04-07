# bot/utils.py

import requests

# Optional: you can use OpenWeatherMap API or any weather service
API_KEY = "28b970111ddad32e8644cc3c2b71153c"

def get_weather(city: str) -> str:
    """Fetch weather for a city."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or "main" not in data:
            return "❌ Could not find weather for that city."

        temp = data['main']['temp']
        description = data['weather'][0]['description'].capitalize()
        feels_like = data['main']['feels_like']

        weather_report = (
            f"🌍 *Weather in {city.title()}*\n\n"
            f"🌡️ Temperature: {temp}°C\n"
            f"🤔 Feels like: {feels_like}°C\n"
            f"☁️ Condition: {description}"
        )
        return weather_report
    except Exception as e:
        return "⚠️ Error fetching weather data."
