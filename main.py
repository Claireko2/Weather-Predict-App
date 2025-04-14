from fastapi import FastAPI
from weather_collector import fetch_weather_data
from predictor import train_model, predict_rain
from db import insert_weather_data
import ssl
import edgedb
from contextlib import asynccontextmanager
from weather_collector import fetch_weather_data, get_timestamp


# Create the EdgeDB client without ssl_context
client = edgedb.create_client(
    dsn="edgedb://user:@localhost:10701/main?sslmode=disable"
)

# Initialize FastAPI
app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup code (this replaces "on_event('startup')")
    print("App startup")
    yield
    # Cleanup code (this replaces "on_event('shutdown')")
    print("App shutdown")

# Use lifespan event handler for setup/cleanup
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.get("/collect")
async def collect_weather(lat: float, lon: float):
    # Fetch weather data from external API
    weather_data = await fetch_weather_data(lat, lon)
    
    # Insert weather data into the database
    await insert_weather_data(weather_data)
    
    # Make rain prediction based on the weather data
    prediction = predict_rain({
        'temperature': weather_data['temperature'],
        'humidity': weather_data['humidity'],
        'pressure': weather_data['pressure']
    })
    
    # Return the collected weather data and prediction
    return {"data": weather_data, "rain_prediction": prediction}

# Example of querying EdgeDB
@app.get("/db-test")
async def db_test():
    records = client.query("""
        SELECT User { name, email }
    """)
    return {"records": records}
