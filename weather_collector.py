import os
os.environ.pop("SSL_CERT_FILE", None)
import asyncio
import httpx
from datetime import datetime

API_KEY = ""
    
async def fetch_weather_data(lat: float, lon: float):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url)
        data = response.json()

        # Extract relevant data from the API response
        weather_data = {
            "timestamp": datetime.utcnow().isoformat(),  # Current timestamp in UTC
            "temperature": data["main"]["temp"],  # Current temperature
            "feels_like": data["main"]["feels_like"],  # "Feels like" temperature
            "temp_min": data["main"]["temp_min"],  # Minimum temperature
            "temp_max": data["main"]["temp_max"],  # Maximum temperature
            "humidity": data["main"]["humidity"],  # Humidity percentage
            "pressure": data["main"]["pressure"],  # Atmospheric pressure
            "wind_speed": data["wind"]["speed"],  # Wind speed
            "wind_deg": data["wind"]["deg"],  # Wind direction
            "wind_gust": data["wind"].get("gust", 0.0),  # Wind gust speed
            "cloud_coverage": data["clouds"]["all"],  # Cloud coverage percentage
            "rainfall": data.get("rain", {}).get("1h", 0.0),  # Rainfall (1 hour)
            "city": data["name"],  # City name
            "latitude": lat,  # Latitude of the location
            "longitude": lon  # Longitude of the location
            
        }
        print(weather_data)  # Debugging step
        return weather_data

# This function returns a timestamp from the API data
def get_timestamp(raw_data: dict):
    return datetime.utcfromtimestamp(raw_data["dt"])


# Function to fetch historical weather data
async def fetch_historical_weather_data(lat: float, lon: float, start_timestamp: int, end_timestamp: int):
    url = f"https://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start_timestamp}&end={end_timestamp}&appid={API_KEY}"
    
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url)
        data = response.json()

        # Extract city_id from the response
        city_id = data["city_id"]
        
        # Fetch current weather data using the city_id to get the city name
        city_name = await get_city_name_by_coordinates(lat, lon)

        # Extract weather data from the response
        historical_weather_data = []

        for entry in data.get("list", []):
            weather_entry = {
                "timestamp": datetime.utcfromtimestamp(entry["dt"]).isoformat(),
                "temperature": entry["main"]["temp"],
                "feels_like": entry["main"]["feels_like"],
                "temp_min": entry["main"]["temp_min"],
                "temp_max": entry["main"]["temp_max"],
                "pressure": entry["main"]["pressure"],
                "humidity": entry["main"]["humidity"],
                "wind_speed": entry["wind"]["speed"],
                "wind_deg": entry["wind"]["deg"],
                "rainfall": entry.get("rain", {}).get("1h", 0.0),  # Rainfall (1 hour)
                "city": city_name,  # Use the city name from the response
                "latitude": lat,
                "longitude": lon
            }
            historical_weather_data.append(weather_entry)

        return historical_weather_data

# Function to get the city name by latitude and longitude (instead of city_id)
async def get_city_name_by_coordinates(lat: float, lon: float):
    print(f"Fetching weather data for coordinates: {lat}, {lon}")  # Print the coordinates to check

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url)
        data = response.json()

        # Debugging step: print the entire response to check for the structure
        print("Response from OpenWeatherMap API:", data)

        # Check if the response contains the 'name' key
        if "name" in data:
            return data["name"]  # Return the city name
        else:
            raise ValueError(f"City name not found in the response for coordinates ({lat}, {lon}). Response: {data}")


