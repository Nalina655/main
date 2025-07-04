# -*- coding: utf-8 -*-
"""Copy of rapid.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Oo2TKPqcaQJys04A-BPEP2HkgSTPlhW9
"""

pip install gtfs-realtime-bindings requests

import time
import requests
from google.transit import gtfs_realtime_pb2

# ======== 🔐 API KEYS ===========
MTA_API_KEY = "bab3392b-58f0-42c2-8b61-421d6a03e72e"
TOMTOM_API_KEY = "gmKSHRhMEQ1oXOnhV5wKL2B3WE45SZL9"
OPENWEATHER_API_KEY = "d7836e8948f06edd3c191fa978ff266f"


# ======== 🌐 API URLs ===========
MTA_API_URL = "https://gtfsrt.prod.obanyc.com/vehiclePositions"
TOMTOM_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# ======== 🚍 MTA GTFS Bus Fetch ===========
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
                "trip_id": v.trip.trip_id,
                "route_id": v.trip.route_id,
                "latitude": v.position.latitude,
                "longitude": v.position.longitude,
                "timestamp": v.timestamp,
                "speed": v.position.speed if v.position.HasField("speed") else None
            })
    return buses

# ======== 🚗 TomTom Traffic Fetch ===========
def fetch_traffic(lat, lon):
    params = {
        "point": f"{lat},{lon}",
        "unit": "KMPH",
        "key": TOMTOM_API_KEY
    }
    r = requests.get(TOMTOM_URL, params=params)
    if r.status_code == 200:
        d = r.json()
        return {
            "current_speed": d["flowSegmentData"]["currentSpeed"],
            "free_flow_speed": d["flowSegmentData"]["freeFlowSpeed"],
            "traffic_ratio": round(d["flowSegmentData"]["currentTravelTime"] / d["flowSegmentData"]["freeFlowTravelTime"], 2)
        }
    return None

# ======== 🌦 OpenWeather Fetch ===========
def fetch_weather(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    r = requests.get(OPENWEATHER_URL, params=params)
    if r.status_code == 200:
        d = r.json()
        return {
            "temperature": d["main"]["temp"],
            "humidity": d["main"]["humidity"],
            "weather": d["weather"][0]["main"],
            "wind_speed": d["wind"]["speed"]
        }
    return None

# ======== 🔁 Loop to Fetch and Print Data ===========
def poll_data():
    while True:
        print("\n=== Fetching real-time bus + traffic + weather data ===")
        buses = fetch_mta_data()
        for bus in buses[:5]:  # Limit for demo
            lat = bus["latitude"]
            lon = bus["longitude"]

            traffic = fetch_traffic(lat, lon)
            weather = fetch_weather(lat, lon)

            print(f"\n🚌 Bus ID: {bus['vehicle_id']}")
            print(f"📍 Location: ({lat}, {lon})")
            print(f"🕒 Timestamp: {bus['timestamp']}")
            print(f"🚗 Traffic: {traffic}")
            print(f"🌦 Weather: {weather}")

        time.sleep(30)

# ======== 🚀 Main ===========
if __name__ == "__main__":
    poll_data()

import time
import requests
import pandas as pd
from datetime import datetime
from google.transit import gtfs_realtime_pb2

# API KEYS
MTA_API_KEY = "bab3392b-58f0-42c2-8b61-421d6a03e72e"
TOMTOM_API_KEY = "gmKSHRhMEQ1oXOnhV5wKL2B3WE45SZL9"
OPENWEATHER_API_KEY = "d7836e8948f06edd3c191fa978ff266f"

# API URLs
MTA_API_URL = "https://gtfsrt.prod.obanyc.com/vehiclePositions"
TOMTOM_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# Fetch bus data
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
                "trip_id": v.trip.trip_id,
                "route_id": v.trip.route_id,
                "latitude": v.position.latitude,
                "longitude": v.position.longitude,
                "timestamp": datetime.utcfromtimestamp(v.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                "raw_unix": v.timestamp,
                "speed": v.position.speed if v.position.HasField("speed") else None
            })
    return buses

# Traffic fetch
def fetch_traffic(lat, lon):
    params = {
        "point": f"{lat},{lon}",
        "unit": "KMPH",
        "key": TOMTOM_API_KEY
    }
    r = requests.get(TOMTOM_URL, params=params)
    if r.status_code == 200:
        d = r.json()
        return {
            "current_speed": d["flowSegmentData"]["currentSpeed"],
            "free_flow_speed": d["flowSegmentData"]["freeFlowSpeed"],
            "traffic_ratio": round(d["flowSegmentData"]["currentTravelTime"] / d["flowSegmentData"]["freeFlowTravelTime"], 2)
        }
    return None

# Weather fetch
def fetch_weather(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    r = requests.get(OPENWEATHER_URL, params=params)
    if r.status_code == 200:
        d = r.json()
        return {
            "temperature": d["main"]["temp"],
            "humidity": d["main"]["humidity"],
            "weather": d["weather"][0]["main"],
            "wind_speed": d["wind"]["speed"]
        }
    return None

# Main loop: fetch + append to CSV
def poll_and_save_to_csv(output_csv="bus_data_log.csv"):
    all_data = []
    for _ in range(10):  # collect 10 cycles (adjust as needed)
        buses = fetch_mta_data()
        for bus in buses[:5]:  # test on 5 buses max
            lat = bus["latitude"]
            lon = bus["longitude"]
            traffic = fetch_traffic(lat, lon)
            weather = fetch_weather(lat, lon)

            row = {
                **bus,
                "traffic_current_speed": traffic["current_speed"] if traffic else None,
                "traffic_ratio": traffic["traffic_ratio"] if traffic else None,
                "temp": weather["temperature"] if weather else None,
                "weather": weather["weather"] if weather else None,
                "humidity": weather["humidity"] if weather else None,
                "wind_speed": weather["wind_speed"] if weather else None
            }
            all_data.append(row)

        print("✅ Data fetched and cached. Waiting for next cycle...")
        time.sleep(30)

    df = pd.DataFrame(all_data)
    df.to_csv(output_csv, index=False)
    print(f"\n📁 Data saved to {output_csv}")

if __name__ == "__main__":
    poll_and_save_to_csv()