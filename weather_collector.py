import os
os.environ.pop("SSL_CERT_FILE", None)

import httpx
from datetime import datetime

API_KEY = "da873be98c6b9f980bc9bb83eb8b9714"

async def fetch_weather_data(lat: float, lon: float):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url)
        data = response.json()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "rainfall": data.get("rain", {}).get("1h", 0.0),
            "city": data["name"]
        }
def get_timestamp(raw_data: dict):
    return datetime.utcfromtimestamp(raw_data["dt"])
