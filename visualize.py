import asyncio
import requests
import matplotlib.pyplot as plt
import pandas as pd
import edgedb
from ipywidgets import Button, VBox, Output
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot
from IPython.display import HTML, display

# Your existing fetch function (fixed to convert DataFrame to list of dicts)
async def fetch_weather_data_from_db(client: edgedb.AsyncIOClient):
    records = await client.query("""
        SELECT WeatherData {
            timestamp,
            temperature,
            humidity,
            rainfall,
            predicted_rain_chance
        }
        ORDER BY timestamp DESC
    """)
    if not records:
        print("[WARN] No weather data available.")
        return None

    # Convert EdgeDB records to list of dictionaries (like API format)
    weather_data = []
    for r in records:
        weather_data.append({
            "timestamp": str(r.timestamp),
            "temperature": float(r.temperature - 273.15) if r.temperature else 0.0,
            "humidity": float(r.humidity) if r.humidity else 0.0,
            "rainfall": float(r.rainfall) if r.rainfall else 0.0,
            "predicted_rain_chance": float(r.predicted_rain_chance * 100) if r.predicted_rain_chance else None
        })
    
    return weather_data

def plot_weather_data_interactive(weather_data): 
    if not weather_data:
        return "<p>No data to plot</p>"
    
    # Convert the weather data to a DataFrame
    df = pd.DataFrame(weather_data)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Handle timezone conversion safely
    if df['timestamp'].dt.tz is None:
        # If no timezone info, assume UTC
        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
    
    # Convert to Pacific Time
    df['timestamp'] = df['timestamp'].dt.tz_convert('America/Vancouver')
    
    # Sort by timestamp
    df.sort_values(by='timestamp', inplace=True)
    
   
    if 'temperature' in df.columns:
        # Convert from Kelvin to Celsius
        df['temperature'] = df['temperature'] - 273.15


    # Initialize the figure
    fig = go.Figure()

    # Modern color palette
    colors = {
        'rainfall': '#3498db',
        'rain_chance': '#e74c3c', 
        'temperature': '#f39c12',
        'humidity': '#9b59b6'
    }

    # Plot Actual Rainfall with gradient colors and improved styling
    fig.add_trace(go.Bar(
        x=df['timestamp'],
        y=df['rainfall'],
        name='💧 Actual Rainfall',
        marker=dict(
            color=df['rainfall'],
            colorscale='Blues',
            showscale=False,
            line=dict(color='rgba(52, 152, 219, 0.8)', width=1),
            opacity=0.8
        ),
        hovertemplate='<b>💧 Rainfall</b><br>' +
                      'Time: %{x|%Y-%m-%d %H:%M}<br>' +
                      'Amount: %{y:.1f} mm<br>' +
                      '<extra></extra>',
        yaxis='y1'
    ))

    # Plot Predicted Rain Chance (if available)
    if 'predicted_rain_chance' in df.columns and df['predicted_rain_chance'].notna().any():
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['predicted_rain_chance'],
            name='🔮 Rain Prediction',
            mode='lines+markers',
            line=dict(
                color=colors['rain_chance'], 
                width=3,
                shape='spline'
            ),
            marker=dict(
                size=8,
                symbol='circle',
                line=dict(color='white', width=2)
            ),
            fill='tonexty',
            fillcolor='rgba(231, 76, 60, 0.1)',
            hovertemplate='<b>🔮 Rain Prediction</b><br>' +
                          'Time: %{x|%Y-%m-%d %H:%M}<br>' +
                          'Chance: %{y:.1f}%<br>' +
                          '<extra></extra>',
            yaxis='y2'
        ))

    # Plot Temperature (if available)
    if 'temperature' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['temperature'],
            name='🌡️ Temperature',
            mode='lines+markers',
            line=dict(
                color=colors['temperature'], 
                width=3,
                shape='spline'
            ),
            marker=dict(
                size=8,
                symbol='circle',
                line=dict(color='white', width=2)
            ),
            fill='tonexty',
            fillcolor='rgba(243, 156, 18, 0.1)',
            hovertemplate='<b>🌡️ Temperature</b><br>' +
                          'Time: %{x|%Y-%m-%d %H:%M}<br>' +
                          'Temp: %{y:.1f}°C<br>' +
                          '<extra></extra>',
            yaxis='y3'
        ))

    # Plot Humidity (if available)
    if 'humidity' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['humidity'],
            name='💧 Humidity',
            mode='lines+markers',
            line=dict(
                color=colors['humidity'], 
                width=3,
                shape='spline'
            ),
            marker=dict(
                size=8,
                symbol='diamond',
                line=dict(color='white', width=2)
            ),
            fill='tonexty',
            fillcolor='rgba(155, 89, 182, 0.1)',
            hovertemplate='<b>💧 Humidity</b><br>' +
                          'Time: %{x|%Y-%m-%d %H:%M}<br>' +
                          'Humidity: %{y:.1f}%<br>' +
                          '<extra></extra>',
            yaxis='y4'
        ))

    # Enhanced layout with modern styling
    fig.update_layout(
        # Title with modern styling
        title={
            'text': '🌤️ <b>Weather Dashboard Analytics</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {
                'size': 28,
                'color': '#2c3e50',
                'family': 'Arial Black'
            }
        },
        
        # X-axis styling
        xaxis=dict(
            title={
                'text': '📅 Time',
                'font': {'size': 14, 'color': '#34495e'}
            },
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(236, 240, 241, 0.5)',
            tickfont=dict(color='#34495e', size=11),
            showline=True,
            linewidth=2,
            linecolor='rgba(52, 73, 94, 0.3)',
            # Add range selector for better navigation
            rangeselector=dict(
                buttons=list([
                    dict(count=6, label="6h", step="hour", stepmode="backward"),
                    dict(count=12, label="12h", step="hour", stepmode="backward"),
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="7d", step="day", stepmode="backward"),
                    dict(step="all")
                ]),
                bgcolor="rgba(52, 152, 219, 0.1)",
                bordercolor="rgba(52, 152, 219, 0.3)",
                borderwidth=1,
                font=dict(color='#2c3e50')
            ),
            rangeslider=dict(visible=False),
            type="date"
        ),
        
        # Y-axes with improved styling - fix the range calculation
        yaxis=dict(
            title={
                'text': '💧 Rainfall (mm)', 
                'font': {'size': 14, 'color': colors['rainfall']}
            },
            side='left',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(52, 152, 219, 0.2)',
            tickfont=dict(color=colors['rainfall']),
            showline=True,
            linewidth=2,
            linecolor=colors['rainfall'],
            range=[max(0, df['rainfall'].min() - 2), df['rainfall'].max() + 2] if len(df) > 0 and df['rainfall'].max() > 0 else [0, 10]
        ),
        
        yaxis2=dict(
            title={
                'text': '🔮 Rain Chance (%)', 
                'font': {'size': 14, 'color': colors['rain_chance']}
            },
            overlaying='y', 
            side='right', 
            position=0.85,
            showgrid=False,
            tickfont=dict(color=colors['rain_chance']),
            showline=True,
            linewidth=2,
            linecolor=colors['rain_chance'],
            range=[0, 100]
        ),
        
        yaxis3=dict(
            title={
                'text': '🌡️ Temperature (°C)', 
                'font': {'size': 14, 'color': colors['temperature']}
            },
            overlaying='y', 
            side='right', 
            position=0.92,
            showgrid=False,
            tickfont=dict(color=colors['temperature']),
            showline=True,
            linewidth=2,
            linecolor=colors['temperature'],
            range=[df['temperature'].min() - 3, df['temperature'].max() + 3] if 'temperature' in df.columns and len(df) > 0 else [0, 30]
        ),
        
        yaxis4=dict(
            title={
                'text': '💧 Humidity (%)', 
                'font': {'size': 14, 'color': colors['humidity']}
            },
            overlaying='y', 
            side='right', 
            position=0.98,
            showgrid=False,
            tickfont=dict(color=colors['humidity']),
            showline=True,
            linewidth=2,
            linecolor=colors['humidity'],
            range=[0, 100]
        ),
        
        # Enhanced legend
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="rgba(52, 73, 94, 0.3)",
            font=dict(size=13, color='#2c3e50'),
            itemsizing='constant'
        ),
        
        # Modern color scheme and styling
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='white',
        
        # Hover styling
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="rgba(52, 73, 94, 0.3)",
            font_size=12,
            font_family="Arial",
            font_color='#2c3e50'
        ),
        
        # Margins and sizing
        margin=dict(t=80, b=120, l=70, r=100),
        height=700,
        
        # Template for consistent styling
        template='plotly_white',
        
        # Add subtitle annotation
        annotations=[
            dict(
                text="📈 Real-time weather monitoring with predictions and historical data",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=-0.12,
                xanchor='center', yanchor='top',
                font=dict(size=14, color='#7f8c8d', style='italic')
            )
        ]
    )

    # Custom configuration for better user experience
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'weather_dashboard',
            'height': 700,
            'width': 1200,
            'scale': 2
        },
        'responsive': True
    }

    # Return the plot in HTML with enhanced config
    return plot(fig, output_type='div', include_plotlyjs='cdn', config=config)

# Async wrapper to run in Jupyter
def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

# Create buttons
out = Output()
collect_btn = Button(description="Collect Current Weather 🌦️")
report_btn = Button(description="Regenerate Report 📊")

async def collect_weather(_):
    # Call your local API to collect current weather
    try:
        response = requests.get("http://127.0.0.1:8000/collect")
        response.raise_for_status()
        with out:
            print("Weather collection triggered successfully!")
            print("Data should now be available in the database.")
    except Exception as e:
        with out:
            print(f"[ERROR] Failed to collect weather: {e}")

async def regenerate_report(_):
    try:
        # Re-fetch and plot the weather data from database
        client = edgedb.create_async_client(
            dsn="edgedb://my_user:mypassword@localhost:10702/main?tls_security=insecure"
        )
        
        weather_data = await fetch_weather_data_from_db(client)
        await client.aclose()
        
        with out:
            out.clear_output()
            if weather_data:
                print(f"Found {len(weather_data)} records in database")
                # Display the interactive plot
                plot_html = plot_weather_data_interactive(weather_data)
                display(HTML(plot_html))
            else:
                print("No weather data found in database. Try collecting some data first!")
                
    except Exception as e:
        with out:
            print(f"[ERROR] Failed to generate report: {e}")

# Button callbacks
collect_btn.on_click(lambda b: run_async(collect_weather(b)))
report_btn.on_click(lambda b: run_async(regenerate_report(b)))

# Display buttons and output
VBox([collect_btn, report_btn, out])