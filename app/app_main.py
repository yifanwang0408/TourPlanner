import sys
import os

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # one level up from app/
sys.path.insert(0, root)

# Get absolute path to the backend folder
backend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'backend')
)

# Add backend folder to the front of sys.path
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
import streamlit as st
from hotel_ui import HotelInfo
from weather_ui import WeatherInfo
from direction_ui import DirectionInfo
from flight_ui import FlightInfo
from attractions_ui import AttractionInfo
from restaurant_ui import RestaurantInfo
from dotenv import load_dotenv
from backend.llm import LLM
from backend import tools, utils


if "llm" not in st.session_state:
    load_dotenv(dotenv_path="api_keys.env")
    st.session_state.llm = LLM("open-api-key", "llm-tourplanner")
    st.session_state.llm.get_api_key()
    st.session_state.llm.setup()

if "step" not in st.session_state:
    st.session_state.step = "Home"
    
#setup the ui for other pages
if "hotel_info" not in st.session_state:
    st.session_state.hotel_info = HotelInfo(st.session_state.llm)
    
if "weather_info" not in st.session_state:
    st.session_state.weather_info = WeatherInfo(st.session_state.llm)
    
if "direction_info" not in st.session_state:
    st.session_state.direction_info = DirectionInfo(st.session_state.llm)
    
if "flight_info" not in st.session_state:
    st.session_state.flight_info = FlightInfo(st.session_state.llm)
    
if "attraction_info" not in st.session_state:
    st.session_state.attraction_info = AttractionInfo(st.session_state.llm)
    
if "restaurant_info" not in st.session_state:
    st.session_state.restaurant_info = RestaurantInfo(st.session_state.llm)

def main():
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
    
    if st.session_state.step == "Hotels":
        st.session_state.hotel_info.run()
    
    if st.session_state.step == "Weather":
        st.session_state.weather_info.run()
    
    if st.session_state.step == "Directions":
        st.session_state.direction_info.run()
        
    if st.session_state.step == "Flight":
        st.session_state.flight_info.run()
        
    if st.session_state.step == "Attractions":
        st.session_state.attraction_info.run()
        
    if st.session_state.step == "Restaurants":
        st.session_state.restaurant_info.run()
    
    if st.session_state.step == "Plan":
        st.title("Generate Complete Plan")
        st.text("Enter basic information to get a personalized plan. Be sure to at least include:\n    - Origin\n    - Destination\n    - Trip start time and duration")
        user_input = st.text_area("Input your information here:", key="text_input_area")
        if st.button("Start Plan Generation") and user_input.strip():
            validity, data = tools.validate_user_input(st.session_state.llm.llm, "backend/schemas/user_input.schema.json", user_input)
            if validity == True:
                travel_info = utils.fetch_all_travel_info(data, st.session_state.hotel_info.hotel_lite,st.session_state.flight_info.future_flight, st.session_state.weather_info.weather, st.session_state.attraction_info.attraction_api, st.session_state.restaurant_info.restaurant_api)
                output = tools.generate_plan(st.session_state.llm.llm, user_input, data, travel_info)
                st.write(output)
                if st.button("Restart"):
                    st.session_state.text_input_area = ""
                    st.rerun()
            else:
                st.write(data)
                if st.button("Restart"):
                    st.session_state.text_input_area = ""
                    st.rerun()
    
        
    


if __name__ == "__main__":
    main()