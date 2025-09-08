import ssl
import edgedb
from fastapi import FastAPI, Query
from contextlib import asynccontextmanager
from weather_collector import fetch_weather_data, fetch_historical_weather_data
from predictor import train_model, predict_rain
from db import insert_weather_data
from datetime import datetime
import requests
import json
from typing import Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot
from fastapi.responses import HTMLResponse
import pandas as pd
import base64
import logging
import pytz  
from zoneinfo import ZoneInfo
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from visualize import plot_weather_data_interactive
logging.basicConfig(level=logging.DEBUG)

# Initialize FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="templates")

def init_edgedb(branch="main"):
    return edgedb.create_async_client(
        dsn=f""
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup code (this replaces "on_event('startup')")
    print("App startup")
    app.state.client_main = init_edgedb("main")  # For current weather
    app.state.client_historical = init_edgedb("historical")  # For historical weather
    yield
    # Cleanup code (this replaces "on_event('shutdown')")
    print("App shutdown")
    await app.state.client_main.aclose()
    await app.state.client_historical.aclose()

# Use lifespan event handler for setup/cleanup
app = FastAPI(lifespan=lifespan)

# Function to get the current location (latitude and longitude) based on IP address
def get_ip_location():
    response = requests.get("http://ip-api.com/json/")
    data = response.json()

    return data['lat'], data['lon'],data['city']

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.get("/collect")
async def collect_weather(lat: float = None, lon: float = None):
    # If lat/lon are not provided, fetch based on IP location
    if lat is None or lon is None:
        lat, lon, city = get_ip_location()
        print(f"Fetched IP location - Lat: {lat}, Lon: {lon}")

    try:
        # Fetch weather data from OpenWeatherMap API
        weather_data = await fetch_weather_data(lat, lon)

        # Check if the weather data contains the expected keys
        required_keys = ["temperature", "feels_like", "temp_min", "temp_max", "pressure", "humidity", "wind_speed", "wind_deg", "rainfall"]
        if not all(key in weather_data for key in required_keys):
            raise ValueError("Incomplete weather data received")
        
        # Convert temperatures from Kelvin to Celsius
        temp_fields = ["temperature", "feels_like", "temp_min", "temp_max"]
        for field in temp_fields:
            if field in weather_data and weather_data[field] is not None:
                weather_data[field] = weather_data[field] - 273.15  # Fixed indentation
        # Insert the weather data into EdgeDB
        await insert_weather_data(weather_data, app.state.client_main)

        # Optional: Predict rainfall based on the weather data
        try:
            prediction = predict_rain({
                "temperature": weather_data["temperature"],
                "feels_like": weather_data["feels_like"],
                "temp_min": weather_data["temp_min"],
                "temp_max": weather_data["temp_max"],
                "pressure": weather_data["pressure"],
                "humidity": weather_data["humidity"],
                "wind_speed": weather_data["wind_speed"],
                "wind_deg": weather_data["wind_deg"],
                "rainfall": weather_data["rainfall"]
            })
            return {"status": "success", "prediction": prediction, "weather_data": weather_data}
        except ValueError as e:
            print(f"[Warning] Prediction skipped: {e}")
            return {"status": "success", "prediction": None, "weather_data": weather_data}
    
    except Exception as e:
        print(f"Error fetching or processing weather data: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/collect-historical")
async def collect_historical_weather():
    lat, lon, city = get_ip_location()  # Get the current location based on IP address
    
    # Calculate start and end timestamps (24 hours ago to now)
    end_timestamp = int(datetime.utcnow().timestamp())
    start_timestamp = end_timestamp - 24 * 60 * 60  # 24 hours ago

    # Fetch historical weather data
    historical_weather_data = await fetch_historical_weather_data(lat, lon, start_timestamp, end_timestamp)
    
    # Insert historical weather data into EdgeDB
    await insert_historical_weather_data(historical_weather_data, app.state.client_historical)

    return {"status": "success", "message": "Historical weather data collected and stored"}



@app.get("/visualization", response_class=HTMLResponse)
async def visualization(request: Request):
    lat, lon, city = get_ip_location()
    current_time = datetime.now(ZoneInfo("America/Vancouver")).strftime("%Y-%m-%d %H:%M:%S %Z")

    end_timestamp = int(datetime.utcnow().timestamp())
    start_timestamp = end_timestamp - 24 * 60 * 60
    weather_data = await fetch_historical_weather_data(lat, lon, start_timestamp, end_timestamp)

    if not weather_data:
        return HTMLResponse("<p>No weather data available to visualize.</p>")

    current_weather = await fetch_weather_data(lat, lon)
    current_temp = current_weather.get("temperature", "N/A")
    current_humidity = current_weather.get("humidity", "N/A")
    current_rain = current_weather.get("rain", "0")

    try:
        rain_probability = predict_rain(current_weather)
        rain_forecast = f"{round(rain_probability * 100)}%"
    except:
        rain_forecast = "N/A"

    try:
        await insert_weather_data(current_weather, app.state.client_main)
    except Exception as e:
        logging.error(f"Error inserting weather data into database: {e}")

    plot_html = plot_weather_data_interactive(weather_data)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "city": city,
        "rain_forecast": rain_forecast,
        "current_temp": current_temp,
        "current_humidity": current_humidity,
        "current_rain": current_rain,
        "current_time": current_time,
        "plot_html": plot_html
    })


async def insert_weather_data(weather_data, client):
    try:
        print("Data types of the API response fields:")
        for key, value in weather_data.items():
            print(f"{key}: {type(value)}")

        print("Inserting data:", json.dumps(weather_data, indent=2, default=str))

        # Predict rain before saving
        try:
            rain_probability = predict_rain(weather_data)
            print(f"[INFO] Predicted rain probability: {rain_probability}")
        except Exception as pred_error:
            print(f"[WARN] Could not predict rain: {pred_error}")
            rain_probability = None

        # Optional: delete all previous records (comment out in production)
        await client.execute("DELETE WeatherData;")

        rainfall = weather_data.get("rainfall", 0.0)

        await client.query("""
            INSERT WeatherData {
                city := <str>$city,
                temperature := <float32>$temperature,
                feels_like := <float32>$feels_like,
                temp_min := <float32>$temp_min,
                temp_max := <float32>$temp_max,
                pressure := <int16>$pressure,
                humidity := <int16>$humidity,
                wind_speed := <float32>$wind_speed,
                wind_deg := <int16>$wind_deg,
                timestamp := <str>$timestamp,
                rainfall := <float32>$rainfall,
                predicted_rain_chance := <optional float64>$predicted_rain_chance
            }
        """,
        city=weather_data["city"],
        temperature=weather_data["temperature"],
        feels_like=weather_data["feels_like"],
        temp_min=weather_data["temp_min"],
        temp_max=weather_data["temp_max"],
        pressure=weather_data["pressure"],
        humidity=weather_data["humidity"],
        wind_speed=weather_data["wind_speed"],
        wind_deg=weather_data["wind_deg"],
        timestamp=weather_data["timestamp"],
        rainfall=rainfall,
        predicted_rain_chance=rain_probability)

        print(f"[DEBUG] Successfully inserted weather data with prediction: {rain_probability}")

    except Exception as e:
        print("Error inserting weather data:", e)


async def insert_historical_weather_data(weather_data_list, client):
    for weather_data in weather_data_list:
        try:
            print(f"Inserting historical data: {weather_data}")

            # Ensure rainfall always has a value
            rainfall = weather_data.get("rainfall") or 0.0

            # Convert timestamp (can be int/float epoch or ISO string)
            ts = weather_data["timestamp"]
            if isinstance(ts, (int, float)):
                ts = datetime.utcfromtimestamp(ts)
            elif isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            # Convert temperatures from Kelvin to Celsius
            temp_fields = ["temperature", "feels_like", "temp_min", "temp_max"]
            for field in temp_fields:
                if field in weather_data and weather_data[field] is not None:
                    weather_data[field] -= 273.15
            # Insert into EdgeDB
            await client.query("""
            INSERT WeatherData {
                city := <str>$city,
                temperature := <float32>$temperature,
                feels_like := <float32>$feels_like,
                temp_min := <float32>$temp_min,
                temp_max := <float32>$temp_max,
                pressure := <int16>$pressure,
                humidity := <int16>$humidity,
                wind_speed := <float32>$wind_speed,
                wind_deg := <int16>$wind_deg,
                timestamp := <str>$timestamp,
                rainfall := <float32>$rainfall,
            }
        """,
        city=weather_data["city"],
        temperature=weather_data["temperature"],
        feels_like=weather_data["feels_like"],
        temp_min=weather_data["temp_min"],
        temp_max=weather_data["temp_max"],
        pressure=weather_data["pressure"],
        humidity=weather_data["humidity"],
        wind_speed=weather_data["wind_speed"],
        wind_deg=weather_data["wind_deg"],
        timestamp=weather_data["timestamp"],
        rainfall=rainfall
        )

        except Exception as e:
            print(f"Error inserting historical weather data: {e}")



@app.post("/train-model")
async def train_weather_model():
    lat, lon, city = get_ip_location()

    # Get historical data from EdgeDB
    historical_data = await fetch_historical_weather_data(
        lat, lon,
        start_timestamp=int(datetime.utcnow().timestamp()) - 30 * 24 * 60 * 60,  # last 30 days
        end_timestamp=int(datetime.utcnow().timestamp())
    )

    if not historical_data:
        return {"status": "error", "message": "No historical data available."}

    df = pd.DataFrame(historical_data)
    train_model(df)
    return {"status": "success", "message": "Model trained successfully."}

@app.get("/predict")
async def predict_rainfall():
    try:
        lat, lon, city = get_ip_location()
        weather_data = await fetch_weather_data(lat, lon)

        if not weather_data:
            return {"status": "error", "message": "No current weather data."}

        probability = predict_rain(weather_data)
        return {
            "status": "success",
            "city": city,
            "rain_probability": probability,
            "weather_data": weather_data
        }

    except Exception as e:
        return {"status": "error", "message": f"Prediction failed: {str(e)}"}

def compute_summary_statistics(df: pd.DataFrame):
    """
    Compute mean, max, min, variance for key weather metrics.
    Converts temperature from Kelvin to Celsius.
    """
    if df.empty:
        return {}

    # Convert temperature from Kelvin to Celsius
    if 'temperature' in df.columns:
        df['temperature'] = df['temperature'] - 273.15

    # Compute summary statistics
    summary = df.agg({
        'temperature': ['mean', 'max', 'min', 'var'],
        'humidity': ['mean', 'max', 'min', 'var'],
        'wind_speed': ['mean', 'max', 'min', 'var'],
        'rainfall': ['mean', 'max', 'min', 'var']
    }).round(2)

    return summary.to_dict()

@app.get("/summary_statistics")
async def summary_statistics():
    lat, lon, city = get_ip_location()

    # Fetch last 24h of historical data
    end_timestamp = int(datetime.utcnow().timestamp())
    start_timestamp = end_timestamp - 24 * 60 * 60
    historical_data = await fetch_historical_weather_data(lat, lon, start_timestamp, end_timestamp)

    if not historical_data:
        return {"status": "error", "message": "No historical data available."}

    df = pd.DataFrame(historical_data)
    stats = compute_summary_statistics(df)
    return {"status": "success", "city": city, "summary_statistics": stats}
    

