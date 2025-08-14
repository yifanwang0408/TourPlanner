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
        st.title("Generate Complete Plan")
        st.text("Follow the steps to enter basic info + additional requirements for a personalized plan:")

        if "plan_substep" not in st.session_state:
            st.session_state.plan_substep = 0
        if "user_input" not in st.session_state:
            st.session_state.user_input = ""

        plan_keys = [
            ("origin", "Enter your origin city:"),
            ("destination", "Enter your destination city:"),
            ("start_date", "Enter trip start date (YYYY-MM-DD):"),
            ("duration", "Enter trip duration in days:"),
            ("additional_req", "Enter any additional requirements (hotel preferences, interests, places to visit, etc.):")
        ]

        substep = st.session_state.plan_substep
        key, prompt_text = plan_keys[substep]

        answer = st.text_input(f"Q{substep + 1}: {prompt_text}", key=f"plan_{substep}")

        # Navigation buttons (Reset in the middle)
        cols = st.columns(3)
        with cols[0]:
            if st.button("Back") and substep > 0:
                st.session_state.plan_substep -= 1
                st.rerun()
        with cols[1]:
            if st.button("Reset"):
                st.session_state.plan_substep = 0
                st.session_state.user_input = ""
                st.rerun()
        with cols[2]:
            if st.button("Next") and answer.strip():
                st.session_state.user_input += f"{prompt_text} {answer}\n"
                if substep + 1 < len(plan_keys):
                    st.session_state.plan_substep += 1
                    st.rerun()
                else:
                    st.success("All inputs collected!")

        # Generate plan
        if substep == len(plan_keys) - 1 and answer.strip():
            if st.button("Start Plan Generation"):
                validity, data = tools.validate_user_input(
                    st.session_state.llm.llm,
                    "backend/schemas/user_input.schema.json",
                    st.session_state.user_input
                )
                if validity:
                    travel_info = utils.fetch_all_travel_info(
                        data,
                        st.session_state.hotel_info.hotel_lite,
                        st.session_state.flight_info.future_flight,
                        st.session_state.weather_info.weather,
                        st.session_state.attraction_info.attraction_api,
                        st.session_state.restaurant_info.restaurant_api
                    )
                    output = tools.generate_plan(
                        st.session_state.llm.llm,
                        st.session_state.user_input,
                        data,
                        travel_info
                    )
                    st.write(output)
                else:
                    st.error(data)


if __name__ == "__main__":
    main()
