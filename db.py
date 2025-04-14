import edgedb

client = edgedb.create_async_client()

async def insert_weather_data(data):
    await client.query(
        """
        INSERT WeatherData {
            timestamp := <datetime>$timestamp,
            temperature := <float64>$temperature,
            humidity := <float64>$humidity,
            pressure := <float64>$pressure,
            rainfall := <float64>$rainfall,
            city := <str>$city
        };
        """,
        **data
    )
