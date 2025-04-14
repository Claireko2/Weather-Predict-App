import pandas as pd
from sklearn.linear_model import LogisticRegression
import edgedb

model = None

def train_model():
    global model
    client = edgedb.create_client()
    records = client.query("""
        SELECT WeatherData {
            temperature,
            humidity,
            pressure,
            rainfall
        }
    """)
    df = pd.DataFrame([r.__dict__ for r in records])
    df['rain_label'] = (df['rainfall'] > 0.1).astype(int)
    X = df[['temperature', 'humidity', 'pressure']]
    y = df['rain_label']
    model = LogisticRegression().fit(X, y)

def predict_rain(data):
    X_pred = [[data['temperature'], data['humidity'], data['pressure']]]
    pred = model.predict_proba(X_pred)[0][1]
    return round(pred * 100, 2)
