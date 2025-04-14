import edgedb

client = edgedb.create_async_client()

async def insert_weather_data(data):
    try:
        await client.query("""
            INSERT WeatherData {
                city := <str>$city,
                temperature := <float32>$temperature,
                feels_like := <float32>$feels_like,
                temp_min := <float32>$temp_min,
                temp_max := <float32>$temp_max,
                pressure := <int16>$pressure,
                humidity := <int16>$humidity,
                weather_main := <str>$weather_main,
                weather_description := <str>$weather_description,
                wind_speed := <float32>$wind_speed,
                wind_deg := <int16>$wind_deg,
                timestamp := <datetime>$timestamp
            };
        """, 
        city=data["city"],
        temperature=data["temperature"],
        feels_like=data["feels_like"],
        temp_min=data["temp_min"],
        temp_max=data["temp_max"],
        pressure=data["pressure"],
        humidity=data["humidity"],
        weather_main=data["weather_main"],
        weather_description=data["weather_description"],
        wind_speed=data["wind_speed"],
        wind_deg=data["wind_deg"],
        timestamp=data["timestamp"])
    except Exception as e:
        print(" Error inserting weather data:", e)
