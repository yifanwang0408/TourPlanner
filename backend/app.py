import streamlit as st
from utils import hotel_input_prompt, transfer_interest_id,weather_input_prompt, direction_input_prompt,furture_flight_input_prompt, site_visit_prompt, restaurant_prompt
from travel_api import (Hotel_LiteAPI, Restaurant_API, Weather_WeatherAPI, Directions_OpenRouteService, FutureFlight_Aviationstack, Attractions_API)
from llm import LLM
import tools
from dotenv import load_dotenv
import utils
from places_category_id import site_categories, restaurant_categories, site_categories_str, restaurant_categories_str

if "llm" not in st.session_state:
    load_dotenv(dotenv_path="api_keys.env")
    st.session_state.llm = LLM("open-api-key", "llm-tourplanner")
    st.session_state.llm.get_api_key()
    st.session_state.llm.setup()

#set up api to fetch info
if "hotel_lite" not in st.session_state:
    st.session_state.hotel_lite = Hotel_LiteAPI("Hotel Lite API","https://api.liteapi.travel")
if "weather" not in st.session_state:
    st.session_state.weather = Weather_WeatherAPI("Weather Forecast (OpenWeatherMap)")
if "direction" not in st.session_state:
    st.session_state.direction = Directions_OpenRouteService("Directions (OpenRouteService)")
if "future_flight" not in st.session_state:
    st.session_state.future_flight = FutureFlight_Aviationstack("Future Flight Schedules (Aviationstack)")
if "attraction_api" not in st.session_state:
    st.session_state.attraction_api = Attractions_API("Attractions API")
if "restaurant_api" not in st.session_state:
    st.session_state.restaurant_api = Restaurant_API("Restaurant API")

llm = st.session_state.llm
hotel_lite = st.session_state.hotel_lite
weather = st.session_state.weather
direction = st.session_state.direction
future_flight = st.session_state.future_flight
attraction_api = st.session_state.attraction_api
restaurant_api = st.session_state.restaurant_api

#set up for the prompt class
search_prompt = utils.Prompt_API_Search()

if "step" not in st.session_state:
    st.session_state.step = "Home"

#hotel variable setup
if "hotel_params" not in st.session_state:
    st.session_state.hotel_params={}
if "hotel_substep" not in st.session_state:
    st.session_state.hotel_substep = 0

#weather forecast setup
if "weather_params" not in st.session_state:
    st.session_state.weather_params = {}
if "weather_substep" not in st.session_state:
    st.session_state.weather_substep = 0

#direction setup
if "direction_params" not in st.session_state:
    st.session_state.direction_params = {}
if "direction_substep" not in st.session_state:
    st.session_state.direction_substep = 0

#flight setup
if "flight_params" not in st.session_state:
    st.session_state.flight_params = {}
if "flight_substep" not in st.session_state:
    st.session_state.flight_substep = 0

#attraction setup
if "attraction_params" not in st.session_state:
    st.session_state.attraction_params = {}
if "attraction_substep" not in st.session_state:
    st.session_state.attraction_substep = 0

#restaurant setup
if "restaurant_params" not in st.session_state:
    st.session_state.restaurant_params = {}
if "restaurant_substep" not in st.session_state:
    st.session_state.restaurant_substep = 0

#used for plan generation
if "text_input_area" not in st.session_state:
    st.session_state.text_input_area = ""


option = st.sidebar.selectbox("Choose The Service You Want:", 
                    ("1. Search Hotels",
                    "2. Get Weather Forecast",
                    "3. Get Directions",
                    "4. Get Future Flight Schedules",
                    "5. Get Attractions",
                    "6. Get Restaurants",
                    "7. Generate Complete Plan",
                    "8. Return to Home Page"))
continue_button = st.sidebar.button("Continue")
if continue_button:
    if option == "1. Search Hotels":
        st.session_state.step = "Hotels"
    elif option == "2. Get Weather Forecast":
        st.session_state.step = "Weather"
    elif option == "3. Get Directions":
        st.session_state.step = "Directions"
    elif option == "4. Get Future Flight Schedules":
        st.session_state.step = "Flight"
    elif option == "5. Get Attractions":
        st.session_state.step = "Attractions"
    elif option == "6. Get Restaurants":
        st.session_state.step = "Restaurants"
    elif option == "7. Generate Complete Plan":
        st.session_state.step = "Plan"
    elif option == "8. Return to Home Page":
        st.session_state.step = "Home"

#Home page -- choice 8
if st.session_state.step == "Home":
    st.title("Tour Planner")
    st.text("This is a app that helps people who want to travel to find personalized tour plan.")
    image_url = "https://assets.thehansindia.com/h-upload/2019/12/27/248830-worldtour.webp"
    st.image(image_url, caption="Home page image")

#Hotel page -- choice 1
if st.session_state.step == "Hotels":

    st.title("Get Hotel")
    st.text("Follow the steps to fetch hotel information")

    substep = st.session_state.hotel_substep
    keys = ["city", "countryCode", "minRating", "starRating"]
    # If we still have questions
    if substep < len(keys):
        key = keys[substep]
        st.write(f"Q{substep + 1}: {hotel_input_prompt[key]}")
        answer = st.text_input("Please Enter:", key=f"hotel_{substep}")

        cols = st.columns(4)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.hotel_substep > 0:
                st.session_state.hotel_substep -= 1
                st.rerun()

        with cols[3]:
            if st.button("Next") and answer.strip():
                st.session_state.hotel_params[key] = answer
                st.session_state.hotel_substep += 1
                st.rerun()

    else:
        # All questions answered
        st.success("All questions answered!")
        st.session_state.hotel_params["limit"] = 5
        validity, message, invalid_fields = tools.validate_user_input_single_api_call(llm.llm, "hotel", st.session_state.hotel_params)
        if validity == True:
            travel_info = hotel_lite.get_hotel_list(url="https://api.liteapi.travel/v3.0/data/hotels",params=st.session_state.hotel_params)
            summary = tools.generate_travel_info_search_summary(llm.llm, "hotel", travel_info, st.session_state.hotel_params)
            st.write(summary)
        else:
            st.write(message)


        if st.button("Restart"):
            st.session_state.hotel_substep = 0
            st.session_state.hotel_params = {}
            st.rerun()

# Get Weather Forecast
if st.session_state.step == "Weather":
    st.title("Get Weather Forecast")
    st.text("Follow the steps to fetch Weather Forecast information")

    substep = st.session_state.weather_substep
    keys = ["city", "date"]
    if substep < len(keys):
        key = keys[substep]
        st.write(f"Q{substep + 1}: {weather_input_prompt[key]}")
        answer = st.text_input("Please Enter:", key=f"weather_{substep}")

        cols = st.columns(4)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.weather_substep > 0:
                st.session_state.weather_substep -= 1
                st.rerun()

        with cols[3]:
            if st.button("Next") and answer.strip():
                st.session_state.weather_params[key] = answer
                st.session_state.weather_substep += 1
                st.rerun()

    else:
        # All questions answered
        st.success("All questions answered!")
        st.session_state.hotel_params["limit"] = 5
        validity, message, invalid_fields = tools.validate_user_input_single_api_call(llm.llm, "weather", st.session_state.weather_params)
        if validity == True:
            travel_info = weather.get_forecast(st.session_state.weather_params)
            summary = tools.generate_travel_info_search_summary(llm.llm, "weather", travel_info, st.session_state.weather_params)
            st.write(summary)
        else:
            st.write(message)

        if st.button("Restart"):
            st.session_state.weather_substep = 0
            st.session_state.weather_params = {}
            st.rerun()

# Get Directions -- choice 3
if st.session_state.step == "Directions":
    st.title("Get Directions")
    st.text("Follow the steps to fetch Directions")
    substep = st.session_state.direction_substep
    keys  = ["start_lon", "start_lat", "end_lon", "end_lat"]
    if substep < len(keys):
        key = keys[substep]
        st.write(f"Q{substep + 1}: {direction_input_prompt[key]}")
        answer = st.text_input("Please Enter:", key=f"direction_{substep}")

        cols = st.columns(4)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.direction_substep > 0:
                st.session_state.direction_substep -= 1
                st.rerun()

        with cols[3]:
            if st.button("Next") and answer.strip():
                st.session_state.direction_params[key] = answer
                st.session_state.direction_substep += 1
                st.rerun()

    else:
        # All questions answered
        st.success("All questions answered!")
        validity, message, invalid_fields =  tools.validate_user_input_single_api_call(llm.llm, "direction", st.session_state.direction_params)
        if validity == True:
            travel_info = direction.get_directions(st.session_state.direction_params)
            summary = tools.generate_travel_info_search_summary(llm.llm, "direction", travel_info, st.session_state.direction_params)
            st.write(summary)
        else:
            st.write(message)

        if st.button("Restart"):
            st.session_state.direction_substep = 0
            st.session_state.direction_params = {}
            st.rerun()

# Get future flight -- choice 4
if st.session_state.step == "Flight":
    st.title("Get Future Flight Schedules")
    st.text("Follow the steps to fetch future flight schedules")
    substep = st.session_state.flight_substep
    keys  = ["airport_dep", "airport_arr", "date_dep", "date_arr"]
    if substep < len(keys):
        key = keys[substep]
        st.write(f"Q{substep + 1}: {furture_flight_input_prompt[key]}")
        answer = st.text_input("Please Enter:", key=f"flight_{substep}")

        cols = st.columns(4)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.flight_substep > 0:
                st.session_state.flight_substep -= 1
                st.rerun()

        with cols[3]:
            if st.button("Next") and answer.strip():
                st.session_state.flight_params[key] = answer
                st.session_state.flight_substep += 1
                st.rerun()

    else:
        # All questions answered
        st.success("All questions answered!")
        validity, message, invalid_fields = tools.validate_user_input_single_api_call(llm.llm, "flight", st.session_state.flight_params)
        if validity == True:
            travel_info = future_flight.get_future_flight_schedules(st.session_state.flight_params)
            summary = tools.generate_travel_info_search_summary(llm.llm, "flight", travel_info, st.session_state.flight_params)
            st.write(summary)
        else:
            st.write(message)

        if st.button("Restart"):
            st.session_state.flight_substep = 0
            st.session_state.flight_params = {}
            st.rerun()

# Get atttractions - choice 5
if st.session_state.step == "Attractions":
    st.title("Get Attractions")
    st.text("Follow the steps to fetch attractions")
    substep = st.session_state.attraction_substep
    keys = ["city", "additional_info", "interest"]
    if substep < len(keys):
        key = keys[substep]
        st.write(f"Q{substep + 1}: {site_visit_prompt[key]}")
        answer = st.text_input("Please Enter:", key=f"attraction_{substep}")

        cols = st.columns(4)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.attraction_substep > 0:
                st.session_state.attraction_substep -= 1
                st.rerun()

        with cols[3]:
            if st.button("Next") and answer.strip():
                if key == "interest":
                    interests = tools.categorize_user_input(llm.llm, answer, site_categories_str)
                    st.session_state.attraction_params["category"] = transfer_interest_id(interests["categories"],site_categories)
                else:
                    st.session_state.attraction_params[key] = answer
                st.session_state.attraction_substep += 1
                st.rerun()

    else:
        # All questions answered
        st.success("All questions answered!")
        response  = tools.city_to_latlon(llm.llm, st.session_state.attraction_params["city"], st.session_state.attraction_params["additional_info"])
        st.session_state.attraction_params["ll"] = response["ll"]
        st.session_state.attraction_params["radius"] = response["radius"]
        travel_info = attraction_api.get_attractions(st.session_state.attraction_params, limit=5)
        summary = tools.generate_travel_info_search_summary(llm.llm, "site", travel_info, st.session_state.attraction_params)
        st.write(summary)
        if st.button("Restart"):
            st.session_state.attraction_substep = 0
            st.session_state.attraction_params = {}
            st.rerun()

# Get restaurant -- choice 6
if st.session_state.step == "Restaurants":
    st.title("Get Restaurants")
    st.text("Follow the steps to fetch restaurants")
    substep = st.session_state.restaurant_substep
    keys = ["city", "additional_info", "food_preference"]
    if substep < len(keys):
        key = keys[substep]
        st.write(f"Q{substep + 1}: {restaurant_prompt[key]}")
        answer = st.text_input("Please Enter:", key=f"restaurant_{substep}")

        cols = st.columns(4)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.restaurant_substep > 0:
                st.session_state.restaurant_substep -= 1
                st.rerun()

        with cols[3]:
            if st.button("Next") and answer.strip():
                if key == "food_preference":
                    interests = tools.categorize_user_input(llm.llm, answer, restaurant_categories_str)
                    st.session_state.restaurant_params["fsq_category_ids"] = transfer_interest_id(interests["categories"], restaurant_categories)
                else:
                    st.session_state.restaurant_params[key] = answer
                st.session_state.restaurant_substep += 1
                st.rerun()
    else:
        # All questions answered
        st.success("All questions answered!")
        response  = tools.city_to_latlon(llm.llm, st.session_state.restaurant_params["city"], st.session_state.restaurant_params["additional_info"])
        st.session_state.restaurant_params["ll"] = response["ll"]
        st.session_state.restaurant_params["radius"] = response["radius"]

        travel_info = restaurant_api.get_restaurant(st.session_state.restaurant_params, limit=5)
        summary = tools.generate_travel_info_search_summary(llm.llm, "restaurant", travel_info, st.session_state.restaurant_params)
        st.write(summary)
        if st.button("Restart"):
            st.session_state.restaurant_substep = 0
            st.session_state.restaurant_params = {}
            st.rerun()

# Generate Plan -- choice 7
if st.session_state.step == "Plan":
    st.title("Generate Complete Plan")
    st.text("Enter basic information to get a personalized plan. Be sure to at least include:\n    - Origin\n    - Destination\n    - Trip start time and duration")
    user_input = st.text_area("Input your information here:", key="text_input_area")
    if st.button("Start Plan Generation") and user_input.strip():
        validity, data = tools.validate_user_input(llm.llm, "backend/schemas/user_input.schema.json", user_input)
        if validity == True:
            travel_info = utils.fetch_all_travel_info(data, hotel_lite, future_flight, weather, attraction_api, restaurant_api)
            output = tools.generate_plan(llm.llm, user_input, data, travel_info)
            st.write(output)
            if st.button("Restart"):
                st.session_state.text_input_area = ""
                st.rerun()
        else:
            st.write(data)
            if st.button("Restart"):
                st.session_state.text_input_area = ""
                st.rerun()
            

    
