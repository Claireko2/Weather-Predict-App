import asyncio
from weather_collector import fetch_weather_data
from db import insert_weather_data

async def job():
    city = "Vancouver"
    data = await fetch_weather_data(city)
    await insert_weather_data(data)
    print("Data inserted")

if __name__ == "__main__":
    asyncio.run(job())
