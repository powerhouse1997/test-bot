import requests
from datetime import datetime, timedelta

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

def parse_reminder_time(reminder_str: str) -> datetime:
    """Parse a reminder time from a string."""
    try:
        # Example: 'in 10 minutes' or 'in 2 hours'
        if 'minute' in reminder_str:
            minutes = int(reminder_str.split()[1])
            return datetime.now() + timedelta(minutes=minutes)
        elif 'hour' in reminder_str:
            hours = int(reminder_str.split()[1])
            return datetime.now() + timedelta(hours=hours)
        elif 'day' in reminder_str:
            days = int(reminder_str.split()[1])
            return datetime.now() + timedelta(days=days)
        else:
            return None  # Return None or handle other formats as necessary
    except Exception as e:
        return None  # In case of error, return None or handle it as needed
