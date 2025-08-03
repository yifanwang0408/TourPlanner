hotel_input_prompt = {
    "city": "Enter city: ",
    "countryCode": "Enter countryCode of where the city is located in: ",
    "hotelName": "Enter hotel name: ",
    "minRating": "Enter the minimum rating of the hotel: ",
    "starRating": "Enter the star rating of the hotel(star ratings have 2 allowed decimals '.0' and '.5' from 1 to 5. e.g. '3.5,4.0,5.0'): "
}

weather_input_prompt = {
    "city": "Enter city: ",
    "date": "Enter date (YYYY-MM-DD): "
}

direction_input_prompt = {
    "start_lon": "Enter start longitude: ",
    "start_lat": "Enter start latitude: ",
    "end_lon": "Enter end longitude: ",
    "end_lat": "Enter end latitude: "
}

furture_flight_input_prompt = {
    "airport_dep": "Enter departure airport IATA code: ",
    "airport_arr": "Enter arrival airport IATA code: ",
    "date_dep": "Enter departure date (YYYY-MM-DD): ",
    "date_arr": "Enter arrival date (YYYY-MM-DD): "
}


import os

from places_category_id import site_categories
from tools import (categorize_user_input, city_to_latlon,
                   validate_user_input_single_api_call)
from travel_api import FutureFlight_Aviationstack, Hotel_LiteAPI


def reprompt_until_valid(llm, category: str, user_input: dict, prompt_dict: dict, validator_function):
    """
    Keep reprompting user until input is valid.
    """
    validity, message, invalid_fields = validator_function(llm, category, user_input)

    while not validity:
        print(f"\n[!] {message}")
        retry = input("Do you want to re-enter the missing/invalid fields? (yes/no): ").strip().lower()
        if retry not in ["yes", "y"]:
            print("User chose not to re-enter. Aborting.")
            return None

        for field in invalid_fields:
            prompt = prompt_dict.get(field, f"Enter value for {field}: ")
            new_value = input(prompt)
            user_input[field] = new_value

        validity, message, invalid_fields = validator_function(llm, category, user_input)

    return user_input


class Prompt_API_Search():
    def __init__(self):
        pass

    def prompt_hotel(self, llm) -> dict:
        user_input = {
            "city": input(hotel_input_prompt["city"]),
            "countryCode": input(hotel_input_prompt["countryCode"]),
        }
        has_hotel_name = input("Do you have a hotel(name) that you want to look for (yes/no)?: ").strip().lower()
        if has_hotel_name in ["yes", "y"]:
            user_input["hotelName"] = input(hotel_input_prompt["hotelName"])
        user_input["minRating"] = input(hotel_input_prompt["minRating"])
        user_input["starRating"] = input(hotel_input_prompt["starRating"])

        validated_input = reprompt_until_valid(
            llm, "hotel", user_input, hotel_input_prompt, validate_user_input_single_api_call
        )

        if validated_input is None:
            return None

        has_preference = input("Do you have any preference on hotel? e.g. Hotels near Eiffel tower? (yes/no)?: ").strip().lower()
        if has_preference in ["yes", "y"]:
            validated_input["aiSearch"] = input("Enter your preference: ")

        return validated_input

    def prompt_weather(self, llm) -> dict:
        user_input = {
            "city": input(weather_input_prompt["city"]),
            "date": input(weather_input_prompt["date"])
        }
        return reprompt_until_valid(
            llm, "weather", user_input, weather_input_prompt, validate_user_input_single_api_call
        )

    def prompt_direction(self, llm) -> dict:
        user_input = {
            "start_lon": input(direction_input_prompt["start_lon"]),
            "start_lat": input(direction_input_prompt["start_lat"]),
            "end_lon": input(direction_input_prompt["end_lon"]),
            "end_lat": input(direction_input_prompt["end_lat"])
        }
        return reprompt_until_valid(
            llm, "direction", user_input, direction_input_prompt, validate_user_input_single_api_call
        )

    def prompt_furture_flight(self, llm) -> dict:
        user_input = {
            "airport_dep": input(furture_flight_input_prompt["airport_dep"]),
            "airport_arr": input(furture_flight_input_prompt["airport_arr"]),
            "date_dep": input(furture_flight_input_prompt["date_dep"]),
            "date_arr": input(furture_flight_input_prompt["date_arr"])
        }
        return reprompt_until_valid(
            llm, "flight", user_input, furture_flight_input_prompt, validate_user_input_single_api_call
        )

    def prompt_site_visit(self, llm) -> dict:
        params = {}
        city = input("Enter the city that you want to visit: ")
        additional_info = input("Additional info to help us locate the city: ")
        interest = input("Enter your interest (e.g. attraction): ")

        response = city_to_latlon(llm, city, additional_info)
        params["ll"] = response["ll"]
        params["radius"] = response["radius"]

        interests = categorize_user_input(llm, interest)
        params["category"] = transfer_interest_id(interests["categories"])
        return params


def process_hotel_query_params(parsed_input, limit=4, aiSearch=None):
    days = parsed_input["daily_plan"]
    list_params = []
    city_list = []
    for day in days:
        param = {
            "countryCode": day["country_code"],
            "cityName": day["city"],
            "starRatingparam": day["accomondation"]["hotel_rating"],
            "limit": limit
        }
        if day["accomondation"]["hotel_name"]:
            param["hotelName"] = day["accomondation"]["hotel_name"]
        if aiSearch:
            param["aiSearch"] = aiSearch
        list_params.append(param)
        city_list.append(day["city"])
    return list_params, city_list


def process_flight_quary_params(parsed_input):
    list_params = []
    for flight in parsed_input["flights"]:
        list_params.append({
            "airport_dep": flight["departure_iata"],
            "airport_arr": flight["arrival_iata"],
            "date_dep": flight["departure_date"],
            "date_arr": flight["arrival_date"]
        })
    return list_params


def get_weather_params(data):
    list_params = []
    for day in data["daily_plan"]:
        list_params.append({
            "lat": day["city_lat"],
            "lon": day["city_lon"],
            "city": day["city"],
            "date": day["date"]
        })
    return list_params


def transfer_interest_id(interests):
    return ",".join(site_categories[interest] for interest in interests)


def get_site_params(data):
    site_params = []
    keys_list = []
    for day in data["daily_plan"]:
        site_params.append({
            "ll": f"{day['city_lat']},{day['city_lon']}",
            "radius": day["city_radius"],
            "category": transfer_interest_id(day["places_visit"])
        })
        keys_list.append((day["city"], day["date"]))
    return site_params, keys_list


def fetch_all_travel_info(data, hotel, flight, weather, attraction):
    travel_info = {}

    hotel_params, city_list = process_hotel_query_params(data)
    travel_info["hotel"] = hotel.get_hotel("https://api.liteapi.travel/v3.0/data/hotels", hotel_params, city_list)

    flight_params = process_flight_quary_params(data)
    travel_info["flight"] = flight.process_several_flights(flight_params)

    weather_params = get_weather_params(data)
    travel_info["weather"] = weather.get_weather_multidays(weather_params)

    site_params, keys_list = get_site_params(data)
    travel_info["site"] = attraction.get_attraction_list(site_params, keys_list)

    return travel_info
