import pandas as pd
from sklearn.linear_model import LogisticRegression
import edgedb
from typing import Dict, Optional

model: Optional[LogisticRegression] = None

async def train_model():
    global model
    client = edgedb.create_async_client(dsn="edgedb://user:@localhost:10701/main")

    records = await client.query("""
        SELECT WeatherData {
            temperature,
            humidity,
            pressure,
            rainfall
        }
    """)

    if not records:
        print("No training data available.")
        return

    # Convert records to DataFrame
    df = pd.DataFrame([r.__dict__ for r in records])

    # Ensure required columns exist
    if df.empty or df.isnull().any().any():
        print("Training data is incomplete.")
        return

    df['rain_label'] = (df['rainfall'] > 0.1).astype(int)
    X = df[['temperature', 'humidity', 'pressure']]
    y = df['rain_label']

    model = LogisticRegression().fit(X, y)
    print("Rain prediction model trained successfully.")

def predict_rain(data: Dict[str, float]) -> float:
    global model
    if model is None:
        raise ValueError("Model has not been trained. Please call `train_model()` first.")
    
    X_pred = [[data['temperature'], data['humidity'], data['pressure']]]
    pred = model.predict_proba(X_pred)[0][1]
    return round(pred * 100, 2)
