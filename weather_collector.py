import httpx
from datetime import datetime

API_KEY = "da873be98c6b9f980bc9bb83eb8b9714"

async def fetch_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        weather = r.json()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "temperature": weather["main"]["temp"],
        "humidity": weather["main"]["humidity"],
        "pressure": weather["main"]["pressure"],
        "rainfall": weather.get("rain", {}).get("1h", 0.0),
        "city": city
    }
