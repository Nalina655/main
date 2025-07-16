import streamlit as st
import pandas as pd
import numpy as np
import requests
import joblib
from datetime import datetime
import pytz
import gtfs_realtime_pb2
from keras.models import load_model
import folium
from streamlit_folium import folium_static
import os

# === Load LSTM Model ===
model_path = "lstm_eta_model.h5"
if os.path.exists(model_path):
    model = load_model(model_path, compile=False)  # ✅ No compile metrics warning
else:
    raise FileNotFoundError("❌ Model file not found!")

# === Load Scaler and Encoder ===
try:
    scaler = joblib.load("feature_scaler.pkl")
    weather_encoder = joblib.load("weather_encoder.pkl")
except Exception as e:
    raise FileNotFoundError(f"❌ Missing scaler or encoder: {e}")

# === API Keys ===
MTA_API_KEY = "bab3392b-58f0-42c2-8b61-421d6a03e72e"
TOMTOM_API_KEY = "gmKSHRhMEQ1oXOnhV5wKL2B3WE45SZL9"
OPENWEATHER_API_KEY = "d7836e8948f06edd3c191fa978ff266f"

# === API URLs ===
MTA_API_URL = "https://gtfsrt.prod.obanyc.com/vehiclePositions"
TOMTOM_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# === Helper Functions ===
def convert_to_ny(utc_timestamp):
    dt = datetime.utcfromtimestamp(utc_timestamp).replace(tzinfo=pytz.utc)
    return dt.astimezone(pytz.timezone("America/New_York")).strftime("%Y-%m-%d %H:%M:%S")

def fetch_mta_data():
    headers = {"x-api-key": MTA_API_KEY}
    r = requests.get(MTA_API_URL, headers=headers)
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(r.content)
    buses = []
    for entity in feed.entity:
        if entity.HasField("vehicle"):
            v = entity.vehicle
            buses.append({
                "vehicle_id": v.vehicle.id,
                "route_id": v.trip.route_id,
                "trip_id": v.trip.trip_id,
                "latitude": v.position.latitude,
                "longitude": v.position.longitude,
                "timestamp": v.timestamp
            })
    return buses[:10]

def fetch_traffic(lat, lon):
    params = {"point": f"{lat},{lon}", "unit": "KMPH", "key": TOMTOM_API_KEY}
    r = requests.get(TOMTOM_URL, params=params)
    if r.status_code == 200:
        data = r.json()["flowSegmentData"]
        return round(data["currentTravelTime"] / data["freeFlowTravelTime"], 2)
    return 1.0

def fetch_weather(lat, lon):
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    r = requests.get(OPENWEATHER_URL, params=params)
    if r.status_code == 200:
        data = r.json()
        return data["main"]["temp"], data["weather"][0]["main"]
    return 25.0, "Clear"

# === Streamlit App ===
st.set_page_config(page_title="Bus ETA Live Tracker", layout="wide")
st.title("🚌 Real-Time Bus ETA Prediction (LSTM Model)")

bus_data = fetch_mta_data()
table_data = []

if bus_data:
    m = folium.Map(location=[bus_data[0]["latitude"], bus_data[0]["longitude"]], zoom_start=11)

    for bus in bus_data:
        lat, lon = bus["latitude"], bus["longitude"]
        traffic_ratio = fetch_traffic(lat, lon)
        temp, weather = fetch_weather(lat, lon)
        ny_time = convert_to_ny(bus["timestamp"])

        try:
            weather_encoded = weather_encoder.transform([weather])[0]
        except:
            weather_encoded = 0

        # ✅ Simulate real time-series variation
        X_df = pd.DataFrame([
            [traffic_ratio * (1 + i*0.01), temp + i*0.1, weather_encoded]
            for i in range(5)
        ], columns=["traffic_ratio", "temperature", "weather_encoded"])

        X_scaled = scaler.transform(X_df).reshape(1, 5, 3)

        try:
            eta = float(model.predict(X_scaled)[0][0])
            eta = max(0, round(eta))  # Non-negative
        except:
            eta = 0

        popup = (
            f"Bus ID: {bus['vehicle_id']}<br>"
            f"Delay: {eta} sec<br>"
            f"Weather: {weather}<br>"
            f"Traffic: {traffic_ratio}"
        )

        try:
            folium.Marker(
                location=[lat, lon],
                tooltip=bus["vehicle_id"],
                popup=popup,
                icon=folium.Icon(color="blue")
            ).add_to(m)
        except:
            pass

        table_data.append({
            "Bus ID": bus["vehicle_id"],
            "Route": bus["route_id"],
            "Time (NY)": ny_time,
            "ETA Delay (sec)": eta,
            "Traffic Ratio": traffic_ratio,
            "Temperature (°C)": temp,
            "Weather": weather
        })

    # ✅ Fixed: folium_static works
    folium_static(m, width=700, height=500)
    st.subheader("📊 Live ETA Predictions")
    st.dataframe(pd.DataFrame(table_data))
else:
    st.warning("⚠️ No bus data available.")
