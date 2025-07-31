hotel_input_prompt = {"city": "Enter city: ", "countryCode": "Enter countryCode of where the city is located in: ", "hotelName": "Enter hotel name: ", "minRating": "Enter the minimum rating of the hotel: ", "starRating": "Enter the star rating of the hotel(star ratings have 2 allowed decimals '.0' and '.5' from 1 to 5. e.g. '3.5,4.0,5.0'): "}
weather_input_prompt = {"city": "Enter city: "}
direction_input_prompt = {"start_lon": "Enter start longitude: ", "start_lat": "Enter start latitude: ", "end_lon": "Enter end longitude: ", "end_lat": "Enter end latitude: "}
furture_flight_input_prompt = {"airport": "Enter airport IATA code: ", "flight_type": "Enter flight type (arrival/departure): ", "date": "Enter date (YYYY-MM-DD):"}

from tools import categorize_user_input, city_to_latlon
from travel_api import FutureFlight_Aviationstack, Hotel_LiteAPI
import os
from places_category_id import site_categories


class Prompt_API_Search():
    def __init__(self):
        pass

    def prompt_hotel(self) -> dict:
        """
        initial prompt for hotel
        """
        params = {}
        params["city"] = input("Enter city: ")
        params["countryCode"] = input("Enter countryCode of where the city is located in: ")
        has_hotel_name = input("Do you have a hotel(name) that you want to look for (yes/no)?: ")
        if (has_hotel_name.lower() == "yes" or has_hotel_name.lower() == "y"):
            params["hotelName"] = input("Enter hotel name:" )
        params["minRating"] = float(input("Enter the minimum rating of the hotel: "))
        params["starRating"] = float(input("Enter the star rating of the hotel(star ratings have 2 allowed decimals '.0' and '.5' from 1 to 5. e.g. '3.5,4.0,5.0'): "))
        has_preference = input("Do you have any preference on hotel? e.g. Hotels near Eiffel tower? (yes/no)?: ")
        if (has_preference.lower() == "yes" or has_preference.lower() == "y"):
            params["aiSearch"] = input("Enter your preference: ")
        return params

    def prompt_weather(self) -> dict:
        """
        initial prompt for weather
        """
        params = {}
        params["city"] = input("Enter city: ")
        params["date"] = input("Enter date (YYYY-MM-DD): ")
        return params

    def prompt_direction(self) -> dict:
        """
        initial prompt for direction
        """
        params = {}
        params["start_lon"] = float(input("Enter start longitude: "))
        params["start_lat"] = float(input("Enter start latitude: "))
        params["end_lon"] = float(input("Enter end longitude: "))
        params["end_lat"] = float(input("Enter end latitude: "))
        return params

    def prompt_furture_flight(self) -> dict:
        """
        initial prompt for direction
        """
        params = {}
        params["airport_dep"] = input("Enter departure airport IATA code: ")
        params["airport_arr"] = input("Enter arrival airport IATA code: ")
        params["date_dep"] = input("Enter departure date (YYYY-MM-DD): ")
        params["date_arr"] = input("Enter arrival date (YYYY-MM-DD): ")
        return params
    
    def prompt_site_visit(self, llm) -> dict:
        params = {}
        city = input("Enter the city that you want to visit: ")
        additional_info = input("Additional info to help us locate the city: ")
        interest = input("Enter your interest (e.g. attraction): ")

        response  = city_to_latlon(llm, city, additional_info)
        params["ll"] = response["ll"]
        params["radius"] = response["radius"]

        interests = categorize_user_input(llm, interest)
        params["category"] = transfer_interest_id(interests["categories"])
        return params

        


def process_hotel_query_params(parsed_input, limit = 4, aiSearch = None):
    """
    This function is for proces hotel info from Liteapi travel

    Args:
        parsed_input: parsed user input
        limit: number of hotel fetch for each city
        aiSearch: additional requirement on hotel, such as hotel near shopping center

    Return:
        parameters for api call to fetch hotel information and a list of city
    """
    #for each city traveled to, generate query to fetch hotel
    days = parsed_input["daily_plan"]
    list_params = []
    city_list = [] 

    for day in days:
        param = {}
        param["countryCode"] = day["country_code"]
        param["cityName"] = day["city"]
        if day["accomondation"]["hotel_name"] != "":
            param["hotelName"] = day["accomondation"]["hotel_name"]
        param["starRatingparam"] = day["accomondation"]["hotel_rating"]
        param["limit"] = limit
        if aiSearch != None:
            param["aiSearch"] = aiSearch
        list_params.append(param)
        city_list.append(day["city"])
    return list_params, city_list


def process_flight_quary_params(parsed_input):
    list_params = []
    for flight in parsed_input["flights"]:
        param = {}
        param["airport_dep"] = flight["departure_iata"]
        param["airport_arr"] = flight["arrival_iata"]
        param["date_dep"] = flight["departure_date"]
        param["date_arr"] = flight["arrival_date"]
        list_params.append(param)
    return list_params


def get_weather_params(data):
    days = data["daily_plan"]
    list_params = []
    for day in days:
        param = {}
        param["lat"] = day["city_lat"]
        param["lon"] = day["city_lon"]
        param["city"] = day["city"]
        param["date"] = day["date"]
        list_params.append(param)
    return list_params

def transfer_interest_id(interests):
    interest_string = ""
    index = 0
    for interest in interests:
        interest_id = site_categories[interest]
        if index == 0:
            interest_string += interest_id
        else:
            interest_string += "," + interest_id
        index += 1
    return interest_string



def get_site_params(data):
    site_params = []
    keys_list = []
    days = data["daily_plan"]
    for day in days:
        param = {}
        param["ll"] = f"{day['city_lat']},{day['city_lon']}"
        param["radius"] = day["city_radius"]

        param["category"] = transfer_interest_id(day["places_visit"])

        site_params.append(param)
        keys_list.append((day["city"], day["date"]))
    return site_params, keys_list






def fetch_all_travel_info(data, hotel, flight, weather, attraction):
    travel_info = {}
    
    #hotel info
    hotel_params, city_list = process_hotel_query_params(data)
    hotel_list = hotel.get_hotel("https://api.liteapi.travel/v3.0/data/hotels", hotel_params, city_list)
    travel_info["hotel"] = hotel_list

    #flight info
    flight_params = process_flight_quary_params(data)
    flight_list = flight.process_several_flights(flight_params)
    travel_info["flight"] = flight_list

    #weather info
    weather_params = get_weather_params(data)
    weather_list = weather.get_weather_multidays(weather_params)
    travel_info["weather"] = weather_list

    #attraction info
    site_params, keys_list = get_site_params(data)
    site_list = attraction.get_attraction_list(site_params, keys_list)
    travel_info["site"] = site_list

    return travel_info