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
from streamlit_folium import st_folium
import os

# === Load Model and Preprocessors ===
model = load_model("lstm_eta_model.h5", compile=False)
scaler = joblib.load("feature_scaler.pkl")
weather_encoder = joblib.load("weather_encoder.pkl")

# === API KEYS ===
MTA_API_KEY = "bab3392b-58f0-42c2-8b61-421d6a03e72e"
TOMTOM_API_KEY = "gmKSHRhMEQ1oXOnhV5wKL2B3WE45SZL9"
OPENWEATHER_API_KEY = "d7836e8948f06edd3c191fa978ff266f"

# === API URLs ===
MTA_API_URL = "https://gtfsrt.prod.obanyc.com/vehiclePositions"
TOMTOM_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# === Helper Functions ===
def convert_to_ny(utc_timestamp):
    utc_dt = datetime.utcfromtimestamp(utc_timestamp).replace(tzinfo=pytz.utc)
    ny_tz = pytz.timezone("America/New_York")
    return utc_dt.astimezone(ny_tz).strftime("%Y-%m-%d %H:%M:%S")

def fetch_mta_data():
    headers = {"x-api-key": MTA_API_KEY}
    response = requests.get(MTA_API_URL, headers=headers)
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
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
    try:
        params = {"point": f"{lat},{lon}", "unit": "KMPH", "key": TOMTOM_API_KEY}
        r = requests.get(TOMTOM_URL, params=params)
        if r.status_code == 200:
            d = r.json()
            return round(d["flowSegmentData"]["currentTravelTime"] / d["flowSegmentData"]["freeFlowTravelTime"], 2)
    except:
        pass
    return 1.0

def fetch_weather(lat, lon):
    try:
        params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
        r = requests.get(OPENWEATHER_URL, params=params)
        if r.status_code == 200:
            d = r.json()
            return d["main"]["temp"], d["weather"][0]["main"]
    except:
        pass
    return 25.0, "Clear"

# === Streamlit UI ===
st.set_page_config(page_title="Bus ETA Live Tracker", layout="wide")
st.title("🚌 Real-Time Bus ETA Prediction (LSTM Model)")

if "bus_history" not in st.session_state:
    st.session_state["bus_history"] = {}

bus_data = fetch_mta_data()
table_data = []

if bus_data:
    first = bus_data[0]
    m = folium.Map(location=[first["latitude"], first["longitude"]], zoom_start=11)

    for bus in bus_data:
        lat, lon = bus["latitude"], bus["longitude"]
        ts = bus["timestamp"]
        ny_time = convert_to_ny(ts)
        vehicle_id = bus["vehicle_id"]

        traffic_ratio = fetch_traffic(lat, lon)
        temp, weather = fetch_weather(lat, lon)

        try:
            weather_encoded = weather_encoder.transform([weather])[0]
        except:
            weather_encoded = 0

        point = [traffic_ratio, temp, weather_encoded]
        history = st.session_state["bus_history"].get(vehicle_id, [])
        history.append(point)
        st.session_state["bus_history"][vehicle_id] = history[-5:]

        if len(st.session_state["bus_history"][vehicle_id]) < 5:
            eta = 0
        else:
            X_df = pd.DataFrame(st.session_state["bus_history"][vehicle_id], columns=["traffic_ratio", "temperature", "weather_encoded"])
            X_scaled = scaler.transform(X_df).reshape(1, 5, 3)
            eta = model.predict(X_scaled)[0][0]
            eta = max(0, round(float(eta)))

        folium.Marker(
            location=[lat, lon],
            tooltip=vehicle_id,
            popup=f"Bus ID: {vehicle_id}<br>Delay: {eta} sec<br>Weather: {weather}<br>Traffic: {traffic_ratio}",
            icon=folium.Icon(color="blue")
        ).add_to(m)

        table_data.append({
            "Bus ID": vehicle_id,
            "Route": bus["route_id"],
            "Time (NY)": ny_time,
            "ETA Delay (sec)": eta,
            "Traffic Ratio": traffic_ratio,
            "Temperature (°C)": temp,
            "Weather": weather
        })

    st_folium(m, width=700, height=500)
    st.subheader("📊 Live ETA Predictions")
    st.dataframe(pd.DataFrame(table_data))

else:
    st.warning("⚠️ No bus data available.")
