import os
import requests
import pandas as pd
from datetime import datetime, timezone
from time import sleep
from constants.constants import OPENWEATHERMAP_API_KEY, GOOGLE_WEATHER_API_KEY

# List of cities with coordinates
CITY_COORDS = {
    "Garut": (-7.2299, 107.9087),
    "Gowa": (-5.3166, 119.7426),
    "Klaten": (-7.7047, 110.6071),
    "Subang": (-6.5721, 107.7580),
    "Indramayu": (-6.3373, 108.3253),
    "Tasikmalaya": (-7.3274, 108.2208),
}

def fetch_openweathermap(city, lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "city": city,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather_desc": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "clouds": data.get("clouds", {}).get("all", None),
            "source": "OpenWeatherMap"
        }
    else:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "city": city,
            "error": f"OWM HTTP {response.status_code}",
            "source": "OpenWeatherMap"
        }

def fetch_google_weather_api(city, lat, lon):
    url = (
        f"https://weather.googleapis.com/v1/currentConditions:lookup"
        f"?key={GOOGLE_WEATHER_API_KEY}"
        f"&location.latitude={lat}&location.longitude={lon}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        return {
            "timestamp": data.get("currentTime"),
            "city": city,
            "temperature": data.get("temperature", {}).get("degrees"),
            "feels_like": data.get("feelsLikeTemperature", {}).get("degrees"),
            "humidity": data.get("relativeHumidity"),
            "dew_point": data.get("dewPoint", {}).get("degrees"),
            "heat_index": data.get("heatIndex", {}).get("degrees"),
            "wind_chill": data.get("windChill", {}).get("degrees"),
            "uv_index": data.get("uvIndex"),
            "weather_desc": data.get("weatherCondition", {}).get("description", {}).get("text"),
            "weather_type": data.get("weatherCondition", {}).get("type"),
            "wind_speed": data.get("wind", {}).get("speed", {}).get("value"),
            "wind_gust": data.get("wind", {}).get("gust", {}).get("value"),
            "wind_dir_deg": data.get("wind", {}).get("direction", {}).get("degrees"),
            "wind_dir_cardinal": data.get("wind", {}).get("direction", {}).get("cardinal"),
            "precip_prob": data.get("precipitation", {}).get("probability", {}).get("percent"),
            "precip_amount": data.get("precipitation", {}).get("qpf", {}).get("quantity"),
            "visibility": data.get("visibility", {}).get("distance"),
            "cloud_cover": data.get("cloudCover"),
            "air_pressure": data.get("airPressure", {}).get("meanSeaLevelMillibars"),
            "temp_min": data.get("currentConditionsHistory", {}).get("minTemperature", {}).get("degrees"),
            "temp_max": data.get("currentConditionsHistory", {}).get("maxTemperature", {}).get("degrees"),
            "source": "GoogleWeatherAPI"
        }

    else:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "city": city,
            "error": f"Google HTTP {response.status_code}",
            "source": "GoogleWeatherAPI"
        }

def append_to_csv(data, folder):
    os.makedirs(folder, exist_ok=True)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    source = data.get("source", "unknown")
    filepath = os.path.join(folder, f"{source.lower()}_{today}.csv")
    df_new = pd.DataFrame([data])
    if os.path.exists(filepath):
        df_existing = pd.read_csv(filepath)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    df_combined.to_csv(filepath, index=False)

def run_openweathermap():
    for city, (lat, lon) in CITY_COORDS.items():
        data = fetch_openweathermap(city, lat, lon)
        append_to_csv(data, "data/openweathermap")
        sleep(1)  # to avoid hitting rate limits

def run_google_weather():
    for city, (lat, lon) in CITY_COORDS.items():
        data = fetch_google_weather_api(city, lat, lon)
        append_to_csv(data, "data/google_weather")
        sleep(1)  # avoid aggressive querying

if __name__ == "__main__":
    print("[INFO] Collecting OpenWeatherMap data...")
    run_openweathermap()

    print("[INFO] Collecting Google Weather API data...")
    run_google_weather()

    print("[INFO] Data collection complete.")
