import os
import sys

import streamlit as st
from dotenv import load_dotenv

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # one level up from app/
sys.path.insert(0, root)
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from attractions_ui import AttractionInfo
from backend import tools, utils
from backend.llm import LLM
from direction_ui import DirectionInfo
from flight_ui import FlightInfo
from hotel_ui import HotelInfo
from restaurant_ui import RestaurantInfo
from dotenv import load_dotenv
from backend.llm import LLM
from backend import tools, utils
from plan_ui import PlanInfo

from weather_ui import WeatherInfo

# Initialize LLM
if "llm" not in st.session_state:
    load_dotenv(dotenv_path="api_keys.env")
    st.session_state.llm = LLM("open-api-key", "llm-tourplanner")
    st.session_state.llm.get_api_key()
    st.session_state.llm.setup()

# Initialize step
if "step" not in st.session_state:
    st.session_state.step = "Home"

# Initialize other modules
for mod_name, mod_class in [("hotel_info", HotelInfo),
                            ("weather_info", WeatherInfo),
                            ("direction_info", DirectionInfo),
                            ("flight_info", FlightInfo),
                            ("attraction_info", AttractionInfo),
                            ("restaurant_info", RestaurantInfo)]:
    if mod_name not in st.session_state:
        st.session_state[mod_name] = mod_class(st.session_state.llm)

if "plan_info" not in st.session_state:
    st.session_state.plan_info = PlanInfo(st.session_state.llm, st.session_state.hotel_info.hotel_lite, st.session_state.flight_info.future_flight, st.session_state.weather_info.weather, st.session_state.attraction_info.attraction_api, st.session_state.restaurant_info.restaurant_api)

# Sets the background based on the current page (st.session_state.step)
def set_page_background():
    """
    Sets a unique gradient background for each page of the app.
    This version targets the correct main container to override the default theme.
    """
    page_gradients = {
        "Home": "linear-gradient(145deg, #B0C4DE, #50A7C2, #2E8B57, #20B2AA);",
        "Hotels": "linear-gradient(145deg, #34495E, #AE8E6F, #800000, #34495E);",
        "Weather": "linear-gradient(145deg, #FFD700, #87CEEB, #778899, #2F4F4F);",
        "Directions": "linear-gradient(145deg, #F4F4F4, #1E90FF, #32CD32, #696969);",
        "Flight": "linear-gradient(145deg, #FFFFFF, #C0C0C0, #4682B4, #D90429);", 
        "Attractions": "linear-gradient(145deg, #FFD700, #FF7F50, #20B2AA, #1E90FF);", 
        "Restaurants": "linear-gradient(145deg, #F5F5DC, #556B2F, #B22222, #536F2F);",
        "Plan": "linear-gradient(145deg, #FFFACD, #FFC04C, #90EE90, #2E8B57);",
        
    }
    
    current_step = st.session_state.get("step", "Home")
    gradient = page_gradients.get(current_step, page_gradients["Home"])

    page_bg_css = f"""
    <style>
    /* THIS SELECTOR IS THE KEY CHANGE */
    div[data-testid="stAppViewContainer"] {{
        background-image: {gradient} !important;
        background-size: cover;
        background-attachment: fixed;
    }}

    /* This rule styles the sidebar, which was already working */
    
    
    
    </style>
    """
    st.markdown(page_bg_css, unsafe_allow_html=True)


def main():
    #Call the function to set the background on every page load
    set_page_background()

    option = st.sidebar.selectbox("Choose The Service You Want:",
                      ("1. Search Hotels",
                       "2. Get Weather Forecast",
                       "3. Get Directions",
                       "4. Get Future Flight Schedules",
                       "5. Get Attractions",
                       "6. Get Restaurants",
                       "7. Generate Complete Plan",
                       "8. Return to Home Page"),
                      index=None,
                      placeholder="Select a service..."
                      )
    continue_button = st.sidebar.button("Continue")
    if continue_button:
        mapping = {
            "1. Search Hotels": "Hotels",
            "2. Get Weather Forecast": "Weather",
            "3. Get Directions": "Directions",
            "4. Get Future Flight Schedules": "Flight",
            "5. Get Attractions": "Attractions",
            "6. Get Restaurants": "Restaurants",
            "7. Generate Complete Plan": "Plan",
            "8. Return to Home Page": "Home"
        }
        st.session_state.step = mapping[option]
        set_page_background()

    # Home Page
    if st.session_state.step == "Home":
        st.title("Tour Planner")
        st.text("This app helps people find a personalized tour plan.")
        st.image("https://assets.thehansindia.com/h-upload/2019/12/27/248830-worldtour.webp", caption="Home page image")

    # Other modules
    module_mapping = {
        "Hotels": st.session_state.hotel_info,
        "Weather": st.session_state.weather_info,
        "Directions": st.session_state.direction_info,
        "Flight": st.session_state.flight_info,
        "Attractions": st.session_state.attraction_info,
        "Restaurants": st.session_state.restaurant_info
    }

    if st.session_state.step in module_mapping:
        module_mapping[st.session_state.step].run()

    # Plan module
    if st.session_state.step == "Plan":
        st.session_state.plan_info.run()
 

if __name__ == "__main__":
    main()
