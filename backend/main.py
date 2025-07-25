from travel_api import (Hotel_LiteAPI, Hotel_RapidAPI, Weather_OpenWeatherMap, Directions_OpenRouteService, FutureFlight_Aviationstack)
from llm import LLM
import tools
from dotenv import load_dotenv
import utils

def main():
    load_dotenv(dotenv_path="api_keys.env")


    llm = LLM("open-api-key", "llm-tourplanner")
    llm.get_api_key()
    llm.setup()
    

    #set up api to fetch info
    hotel_lite = Hotel_LiteAPI("Hotel Lite API","https://api.liteapi.travel")
    hotel_rapid = Hotel_RapidAPI("Hotel Rapid API")
    weather = Weather_OpenWeatherMap("Weather Forecast (OpenWeatherMap)")
    direction = Directions_OpenRouteService("Directions (OpenRouteService)")
    furture_flight = FutureFlight_Aviationstack("Future Flight Schedules (Aviationstack)")

    #set up for the prompt class
    search_prompt = utils.Prompt_API_Search()
    


    #user input schema
    input_schema = "schemas/user_input_test.schema.json"

    while True:
        print("\n--- Tour Planner CLI ---")
        print("1. Search Hotels")
        print("2. Get Weather Forecast")
        print("3. Get Directions")
        print("4. Get Future Flight Schedules")
        print("5. Generate Complete Plan")
        print("6. Exit")

        choice = input("Choose an option (1-6): ")

        if choice == "1":
            params = search_prompt.prompt_hotel()
            params["limit"] = 3
            validity, message, invalid_fields = tools.validate_user_input_single_api_call(llm.llm, "hotel", params)
            if validity == True:
                travel_info = hotel_lite.get_hotel_list(url="https://api.liteapi.travel/v3.0/data/hotels",params=params)
                summary = tools.generate_travel_info_search_summary(llm.llm, "hotel", travel_info, params)
                print(summary)
            else:
                print(message)
                print(invalid_fields)


        elif choice == "2":
            params = search_prompt.prompt_weather()
            validity, message, invalid_fields = tools.validate_user_input_single_api_call(llm.llm, "weather", params)
            if validity == True:
                travel_info = weather.get_weather_forecast(params)
                summary = tools.generate_travel_info_search_summary(llm.llm, "weather", travel_info, params)
                print(summary)
            else:
                print(message)
                print(invalid_fields)

        elif choice == "3":
            params = search_prompt.prompt_direction()
            validity, message, invalid_fields = tools.validate_user_input_single_api_call(llm.llm, "direction", params)
            if validity == True:
                travel_info = direction.get_directions(params)
                summary = tools.generate_travel_info_search_summary(llm.llm, "direction", travel_info, params)
                print(summary)
            else:
                print(message)
                print(invalid_fields)
            
        elif choice == "4":
            params = search_prompt.prompt_furture_flight()
            validity, message, invalid_fields = tools.validate_user_input_single_api_call(llm.llm, "flight", params)
            if validity == True:
                travel_info = furture_flight.get_future_flight_schedules(params)
                summary = tools.generate_travel_info_search_summary(llm.llm, "flight", travel_info, params)
                print(summary)
            else:
                print(message)
                print(invalid_fields)
        

        elif choice == "5":
            validity = False
            #user input string
            user_input = ""
            while (validity == False):
                #for testing user input
                user_input = user_input + input("input your travel plan and preference: ")
                #call for validation
                validity, data = tools.validate_user_input(llm.llm, input_schema, user_input)
                if(validity == False):
                    print(data)

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
