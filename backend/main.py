from travel_api import (Hotel_LiteAPI, Hotel_RapidAPI, Restaurant_API, Weather_WeatherAPI, Directions_OpenRouteService, FutureFlight_Aviationstack, Attractions_API)
from llm import LLM
import tools
import utils
from dotenv import load_dotenv
from llm import LLM
from travel_api import (Attractions_API, Directions_OpenRouteService,
                        FutureFlight_Aviationstack, Hotel_LiteAPI,
                        Hotel_RapidAPI, Weather_WeatherAPI)


def main():
    load_dotenv(dotenv_path="api_keys.env")

    llm = LLM("open-api-key", "llm-tourplanner")
    llm.get_api_key()
    llm.setup()

    # Set up APIs
    hotel_lite = Hotel_LiteAPI("Hotel Lite API", "https://api.liteapi.travel")
    hotel_rapid = Hotel_RapidAPI("Hotel Rapid API")
    weather = Weather_WeatherAPI("Weather Forecast (OpenWeatherMap)")
    direction = Directions_OpenRouteService("Directions (OpenRouteService)")
    future_flight = FutureFlight_Aviationstack("Future Flight Schedules (Aviationstack)")
    attraction_api = Attractions_API("Attractions API")
    restaurant_api = Restaurant_API("Restaurant API")


    # Prompt setup
    search_prompt = utils.Prompt_API_Search()

    # User input schema path
    input_schema = "backend/schemas/user_input.schema.json"

    while True:
        print("\n--- Tour Planner CLI ---")
        print("1. Search Hotels")
        print("2. Get Weather Forecast")
        print("3. Get Directions")
        print("4. Get Future Flight Schedules")
        print("5. Get Attractions")
        print("6. Get Restaurants")
        print("7. Generate Complete Plan")
        print("8. Exit")

        choice = input("Choose an option (1-8): ")

        if choice == "1":
            params = search_prompt.prompt_hotel(llm.llm)
            params["limit"] = 3
            validity, message, invalid_fields = tools.validate_user_input_single_api_call(llm.llm, "hotel", params)
            if validity:
                travel_info = hotel_lite.get_hotel_list(url="https://api.liteapi.travel/v3.0/data/hotels", params=params)
                summary = tools.generate_travel_info_search_summary(llm.llm, "hotel", travel_info, params)
                print(summary)
            else:
                print(message)
                print(invalid_fields)

        elif choice == "2":
            params = search_prompt.prompt_weather(llm.llm)
            validity, message, invalid_fields = tools.validate_user_input_single_api_call(llm.llm, "weather", params)
            if validity:
                travel_info = weather.get_forecast(params)
                summary = tools.generate_travel_info_search_summary(llm.llm, "weather", travel_info, params)
                print(summary)
            else:
                print(message)
                print(invalid_fields)

        elif choice == "3":
            params = search_prompt.prompt_direction(llm.llm)
            validity, message, invalid_fields = tools.validate_user_input_single_api_call(llm.llm, "direction", params)
            if validity:
                travel_info = direction.get_directions(params)
                summary = tools.generate_travel_info_search_summary(llm.llm, "direction", travel_info, params)
                print(summary)
            else:
                print(message)
                print(invalid_fields)

        elif choice == "4":
            params = search_prompt.prompt_furture_flight(llm.llm)
            validity, message, invalid_fields = tools.validate_user_input_single_api_call(llm.llm, "flight", params)
            if validity:
                travel_info = future_flight.get_future_flight_schedules(params)
                summary = tools.generate_travel_info_search_summary(llm.llm, "flight", travel_info, params)
                print(summary)
            else:
                print(message)
                print(invalid_fields)

        elif choice == "5":
            params = search_prompt.prompt_site_visit(llm.llm)
            travel_info = attraction_api.get_attractions(params, limit=5)
            summary = tools.generate_travel_info_search_summary(llm.llm, "site", travel_info, params)
            print(summary)

        elif choice == "6":
            params = search_prompt.prompt_restaurant(llm.llm)
            travel_info = restaurant_api.get_restaurant(params, limit=5)
            summary = tools.generate_travel_info_search_summary(llm.llm, "restaurant", travel_info, params)
            print(summary)

        elif choice == "7":
            validity = False
            user_input = ""
            while not validity:
                user_input += input("Input your travel plan and preference: ")
                validity, data = tools.validate_user_input(llm.llm, input_schema, user_input)
                if not validity:
                    print(data)
            travel_info = utils.fetch_all_travel_info(data, hotel_lite, future_flight, weather, attraction_api, restaurant_api)
            output = tools.generate_plan(llm.llm, user_input, data, travel_info)
            print(output)
            

        elif choice == "8":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
