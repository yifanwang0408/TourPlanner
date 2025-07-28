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
LITE_API_KEY = os.getenv("LITEAPI_KEY")

AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

class Travel_info():

    def __init__(self, name, base_url=None):
        self.name = name
        self.base_url = base_url
    
    def __str__(self):
        return f"{self.name}"
    
    

class Hotel_LiteAPI(Travel_info):
    def __init__(self, name, base_url=None):
        super().__init__(name, base_url)
        self.info = {}

    def get_hotel_list(self, url: str, params: dict) -> dict:
        """
        The function get a list of hotel with given params

        Args:
            url: url to fetch data
            params: parameter dictionary for request.get
        
        Return:
            the json format retrieved data if successful. otherwise return None
        """
        url = url
        headers = {"accept": "application/json",
                   "X-API-Key": LITE_API_KEY,
                   }
    
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"Fetch hotel error: {e}")
            return None

    def get_hotel(self, url: str, params_list: list, city_list: list) -> dict:
        """
        The function takes a list of params and list of cities, for each city, call the get hotel list function to fetch hotels in this city. 

        Args:
            url: url to fetch data
            param_list: a list of parameters used to fetch data from api
            city_list: a list of cities 
        
        Return: 
            a dictionary of hotel. the key of the dictionary is the city name, and the value is a list of city in this city.
        """
        hotel_list = {}
        index = 0
        for params in params_list:
            response = self.get_hotel_list(url, params)
            hotel_list[city_list[index]] = response
            index += 1
        return hotel_list
    
    def get_hotel_detail(self, hotel_id: str) -> dict:
        """
        This function get detailed hotel information based on the hotel id

        Args:
            hotel_id: the id of the hotel
        
        Return:
            Return a dictionary of hotel information if fetch is successful, otherwise return None.
        """
        url = "https://api.liteapi.travel/v3.0/data/hotel?timeout=4"
        headers = {"accept": "application/json",
                   "X-API-Key": LITE_API_KEY,
                   }
        params = {"hotelId": hotel_id}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"Fetch hotel error: {e}")
            return None
    
# === 1. Hotel Search ===
class Hotel_RapidAPI(Travel_info):
    def __init__(self, name, base_url=None):
        super().__init__(name, base_url)
        self.info = {}


    def search_hotels(self, destination: str, checkin_date: str, checkout_date: str, adults:int =1) -> dict:
        """
        Function search hotels based on given parameters

        Args:
            destination: a string containing the city where the hotel is located in
            checkin_date: a string containing the check-in date in 'YYYY-MM-DD' format
            checkout_date: a string containing the check-out dats in 'YYYY-MM-DD' format
            adult: an integer indicating the number of adult

        Return:
            Return json format data if api fetch is successful, otherwise return None
        """
        self.base_url = f"https://{RAPIDAPI_HOST}/hotels/search"
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
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Hotel API error: {e}")
            return None
    


# === 2. Weather Forecast (OpenWeatherMap) ===
class Weather_OpenWeatherMap(Travel_info):
    def __init__(self, name, base_url=None):
        super().__init__(name, base_url)
        self.info = {}

    def get_weather_forecast(self, params: dict):
        """
        Get the weather forecast 

        Args:
            params: the parameter for api search
        
        Return:
            Return the json data of fetched info if the api fetch is successful. Otherwise return None
        """
        city_name = params["city"]
        self.base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OWM_API_KEY}&units=metric"
        try:
            response = requests.get(self.base_url)
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
class Directions_OpenRouteService(Travel_info):
    def __init__(self, name, base_url=None):
        super().__init__(name, base_url)
        self.info = {}

    def get_directions(self, params: dict):
        """
        Get the direction

        Args:
            start_coords & end_coords format: [longitude, latitude]

        Return:
            Return json data if api fetch is successful. Otherwise, return None.
        """
        self.base_url = "https://api.openrouteservice.org/v2/directions/driving-car"
        headers = {
            "Authorization": ORS_API_KEY,
            "Content-Type": "application/json"
        }

        start_coords = [params["start_lon"], params["start_lat"]]
        end_coords = [params["end_lon"], params["end_lat"]]

        payload = {
            "coordinates": [start_coords, end_coords]
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Directions API error: {e}")
            return None

# === 4. Future Flight Schedules (Aviationstack) ===
class FutureFlight_Aviationstack(Travel_info):
    def __init__(self, name, base_url=None):
        super().__init__(name, base_url)
        self.info = {}

    def get_future_flight_schedules(self, params: dict):
        """
        Fetch future flight schedules from Aviationstack.

        Args:
            iata_code (str): IATA code of airport (e.g., 'JFK')
            flight_type (str): 'departure' or 'arrival'
            date (str): date string in 'YYYY-MM-DD' format

        Returns:
            list: List of flight schedule dicts or None on error
        """
        #self.base_url = "https://api.aviationstack.com/v1/flightsFuture"
        self.base_url = "https://api.aviationstack.com/v1/flights"
        params = {
            "access_key": AVIATIONSTACK_API_KEY,
            "dep_iata": params["airport_dep"],
            "arr_iata": params["airport_arr"],
            "dep_date": params["date_dep"],
            "arr_date": params["date_arr"]
        }
        """
        params = {
            "access_key": AVIATIONSTACK_API_KEY,
            "iataCode": params["airport"],
            "type": params["flight_type"],
            "date": params["date"]
        }
        """
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.exceptions.RequestException as e:
            print(f"Future Flight Schedules API error: {e}")
            return None
    
    def process_several_flights(self, params_list: list):
        flights_output = {} #departure is the key, value is all the flight associated with it
        for param in params_list:
            response = self.get_future_flight_schedules(param)
            flights_output[param["airport_dep"]] = response
        return flights_output

