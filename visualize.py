import pandas as pd
import plotly.express as px
import edgedb

def plot_rainfall():
    client = edgedb.create_client()
    records = client.query("""
        SELECT WeatherData {
            timestamp,
            rainfall,
            city
        } ORDER BY .timestamp DESC LIMIT 100
    """)
    df = pd.DataFrame([r.__dict__ for r in records])
    fig = px.line(df, x="timestamp", y="rainfall", color="city", title="Rainfall Over Time")
    fig.show()
