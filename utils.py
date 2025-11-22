import requests


def get_weather_daily(lat, lon) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "wind_speed_10m",
            "relative_humidity_2m",
            "weather_code"
        ],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max"
        ],
        "timezone": "auto"
    }

    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()

        result = {
            "current": {
                "temperature": data["current"]["temperature_2m"],
                "wind_speed": data["current"]["wind_speed_10m"],
                "humidity": data["current"]["relative_humidity_2m"],
                "weather_code": data["current"]["weather_code"]
            },
            "daily": {
                "temp_max": data["daily"]["temperature_2m_max"][0],
                "temp_min": data["daily"]["temperature_2m_min"][0],
                "rain_chance": data["daily"]["precipitation_probability_max"][0]
            }
        }

        return result

    except Exception as e:
        return {"error": str(e)}
