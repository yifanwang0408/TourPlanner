import os

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === ENV VARS ===
ORS_API_KEY = os.getenv("ORS_API_KEY")
OWM_API_KEY = os.getenv("OWM_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "travel-advisor.p.rapidapi.com")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# === 1. Hotel Search ===
def search_hotels(destination, checkin_date, checkout_date, adults=1):
    url = f"https://{RAPIDAPI_HOST}/hotels/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    params = {
        "query": destination,
        "checkin": checkin_date,
        "checkout": checkout_date,
        "adults": adults
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Hotel API error: {e}")
        return None

# === 2. Weather Forecast (OpenWeatherMap) ===
def get_weather_forecast(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OWM_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            return {
                "description": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"]
            }
        else:
            return {"error": data.get("message", "City not found.")}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# === 3. Directions (OpenRouteService) ===
def get_directions(start_coords, end_coords):
    """
    start_coords & end_coords format: [longitude, latitude]
    """
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "coordinates": [start_coords, end_coords]
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Directions API error: {e}")
        return None

# === 4. Future Flight Schedules (Aviationstack) ===
def get_future_flight_schedules(iata_code, flight_type, date):
    """
    Fetch future flight schedules from Aviationstack.

    Args:
        iata_code (str): IATA code of airport (e.g., 'JFK')
        flight_type (str): 'departure' or 'arrival'
        date (str): date string in 'YYYY-MM-DD' format

    Returns:
        list: List of flight schedule dicts or None on error
    """
    url = "https://api.aviationstack.com/v1/flightsFuture"
    params = {
        "access_key": AVIATIONSTACK_API_KEY,
        "iataCode": iata_code,
        "type": flight_type,
        "date": date
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"Future Flight Schedules API error: {e}")
        return None
