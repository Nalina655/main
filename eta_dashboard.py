import time
import requests
from datetime import datetime, timedelta
from google.transit import gtfs_realtime_pb2
import pytz

# ======== 🔐 API KEYS ===========
MTA_API_KEY = "bab3392b-58f0-42c2-8b61-421d6a03e72e"
TOMTOM_API_KEY = "gmKSHRhMEQ1oXOnhV5wKL2B3WE45SZL9"
OPENWEATHER_API_KEY = "d7836e8948f06edd3c191fa978ff266f"

# ======== 🌐 API URLs ===========
MTA_API_URL = "https://gtfsrt.prod.obanyc.com/vehiclePositions"
TOMTOM_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
REVERSE_GEOCODE_URL = "https://nominatim.openstreetmap.org/reverse"

# ======== ⏱️ Convert to New York Time ===========
def convert_to_ny(utc_timestamp):
    utc_dt = datetime.utcfromtimestamp(utc_timestamp).replace(tzinfo=pytz.utc)
    ny_tz = pytz.timezone("America/New_York")
    ny_time = utc_dt.astimezone(ny_tz)
    return ny_time.strftime("%Y-%m-%d %H:%M:%S %Z")

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

# ======== 🌍 Reverse Geocoding ===========
def get_place_name(lat, lon):
    params = {"lat": lat, "lon": lon, "format": "json"}
    try:
        r = requests.get(REVERSE_GEOCODE_URL, params=params, headers={"User-Agent": "MTA-Bus-Tracker/1.0"})
        if r.status_code == 200:
            data = r.json()
            return data.get("display_name", "Unknown Location")
    except:
        pass
    return "Unknown Location"

# ======== 🚗 TomTom Traffic Fetch ===========
def fetch_traffic(lat, lon):
    params = {"point": f"{lat},{lon}", "unit": "KMPH", "key": TOMTOM_API_KEY}
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
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
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
        for bus in buses[:5]:
            lat = bus["latitude"]
            lon = bus["longitude"]
            place_name = get_place_name(lat, lon)
            ny_time = convert_to_ny(bus["timestamp"])

            traffic = fetch_traffic(lat, lon)
            weather = fetch_weather(lat, lon)

            print(f"\n🚌 Bus ID: {bus['vehicle_id']} | Route: {bus['route_id']} | Trip: {bus['trip_id']}")
            print(f"📍 Location: {place_name} ({lat:.5f}, {lon:.5f})")
            print(f"🕒 Timestamp (New York): {ny_time}")

            if traffic:
                print(f"🚗 Traffic - Current Speed: {traffic['current_speed']} km/h | Free Flow Speed: {traffic['free_flow_speed']} km/h | Ratio: {traffic['traffic_ratio']}")
                if traffic["traffic_ratio"] > 1.1:
                    delay_sec = int((traffic["traffic_ratio"] - 1) * 60)
                    print(f"🕓 Bus likely delayed due to traffic (~{delay_sec} sec)")
            else:
                print("🚗 Traffic data not available.")

            if weather:
                print(f"☁️ Weather - Temp: {weather['temperature']} °C | Humidity: {weather['humidity']}% | Condition: {weather['weather']} | Wind: {weather['wind_speed']} m/s")
                if weather['weather'] in ["Rain", "Snow", "Thunderstorm", "Drizzle"]:
                    print("☔ Weather may cause delays.")
            else:
                print("☁️ Weather data not available.")

        time.sleep(30)

# ======== 🚀 Main ===========
if __name__ == "__main__":
    poll_data()
