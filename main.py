from fastapi import FastAPI
from weather_collector import fetch_weather_data
from predictor import train_model, predict_rain
from db import insert_weather_data
import asyncio

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Initial training (could be moved to another file)
    train_model()

@app.get("/collect")
async def collect(city: str):
    data = await fetch_weather_data(city)
    await insert_weather_data(data)
    prediction = predict_rain(data)
    return {"data": data, "rain_prediction": prediction}
