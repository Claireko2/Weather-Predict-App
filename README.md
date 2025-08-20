# Weather Predict Web App

**Data Analyst | Weather Predict Web App** – Developed in Apr 2025  

A web application that predicts rainfall probability using real-time weather data. Built as a data-driven solution for environmental insights, featuring a full data pipeline, predictive modeling, and interactive visualizations.

---

## Features

- Real-time weather data ingestion via **OpenWeather API**
- Predict rainfall probability using **Logistic Regression** (scikit-learn)
- Interactive visualizations of weather trends using **Plotly** and **Chart.js**
- Data stored and managed in **EdgeDB** and **PostgreSQL** for efficient querying

---

## Technology Stack

- **Programming:** Python  
- **Databases:** EdgeDB, PostgreSQL  
- **Data Analysis & ML:** Pandas, NumPy, scikit-learn  
- **Visualization:** Plotly, Chart.js  
- **API:** OpenWeather API

---

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/YourUsername/WeatherPredict.git
    cd WeatherPredict
    
2. Create a virtual environment:
    ```bash
        python -m venv venv
        venv\Scripts\activate

3. Run the app:
   ```bash
        python app.py
   
4. Open your browser at http://localhost:5000

---

## Workflow
- Data Pipeline: Fetches real-time weather data using OpenWeather API and stores it in EdgeDB.
- Modeling: Logistic Regression model predicts rainfall probability.
- Visualization: Trend analysis and interactive dashboards using Plotly and Chart.js.

---

### Skills
Python, EdgeDB, PostgreSQL, scikit-learn, Pandas, NumPy, Plotly, Chart.js

### Future Enhancements
- Multi-day rainfall prediction
- Deploy on cloud for public access
- Integrate more environmental data sources for richer insights
