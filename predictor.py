import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# Path to save/load model
MODEL_PATH = "rain_model.pkl"

# List of features used for training and prediction
FEATURE_COLUMNS = [
    "temperature", "feels_like", "temp_min", "temp_max",
    "pressure", "humidity", "wind_speed", "wind_deg"
]

def train_model(data: pd.DataFrame):
    """
    Train a machine learning model to predict rainfall.
    Saves the trained model to disk.
    """
    if 'rainfall' not in data.columns:
        raise ValueError("Data must contain 'rainfall' column for training.")

    # Binary classification: 1 if rainfall > 0, else 0
    data["rainfall_label"] = (data["rainfall"] > 0).astype(int)

    X = data[FEATURE_COLUMNS]
    y = data["rainfall_label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("Classification Report:\n", classification_report(y_test, y_pred))

    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"[INFO] Model saved to {MODEL_PATH}")


def predict_rain(weather_features: dict) -> float:
    """
    Predict the probability of rain based on current weather features.
    Returns the rain probability between 0 and 1.
    """
    if not os.path.exists(MODEL_PATH):
        raise ValueError("Model not trained yet. Run train_model first.")

    model = joblib.load(MODEL_PATH)

    # Ensure all required features are present
    missing = [f for f in FEATURE_COLUMNS if f not in weather_features]
    if missing:
        raise ValueError(f"Missing features for prediction: {missing}")

    # Prepare input for prediction
    input_data = pd.DataFrame([{
        feature: weather_features[feature] for feature in FEATURE_COLUMNS
    }])

    probability = model.predict_proba(input_data)[0][1]  # Probability of rain
    return round(probability, 4)

  