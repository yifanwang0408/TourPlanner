import streamlit as st
from backend.utils import fetch_all_travel_info
import backend.tools as tools

class PlanInfo:
    def __init__(self, llm, hotel, future_flight, weather, attraction_api, restaurant_api):

        if "plan_substep" not in st.session_state:
            st.session_state.plan_substep = 0
        if "user_input" not in st.session_state:
            st.session_state.user_input = ""

        self.substep = st.session_state.plan_substep
        self.llm = llm
        self.plan_keys = [
            ("origin", "Enter your origin city:"),
            ("destination", "Enter your destination city:"),
            ("start_date", "Enter trip start date (YYYY-MM-DD):"),
            ("duration", "Enter trip duration in days:"),
            ("additional_req", "Enter any additional requirements (hotel preferences, interests, places to visit, etc.):")
        ]
        self.key_length = len(self.plan_keys)
        self.hotel = hotel
        self.future_flight = future_flight
        self.weather = weather
        self.attraction_api = attraction_api
        self.restaurant_api = restaurant_api

    @staticmethod
    def next_back_button(answer, prompt_text): 
        cols = st.columns(9)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.plan_substep > 0:
                st.session_state.plan_substep -= 1
                st.rerun()

        with cols[8]:
            if st.button("Next") and answer.strip():
                st.session_state.user_input += f"{prompt_text} {answer}\n"
                st.session_state.plan_substep += 1
                st.rerun()

    def present_input(self):
        st.write("Your Input:")
        st.write(st.session_state.user_input)
            
        st.markdown("\n---\n")

    def reset(self):
        st.session_state.plan_substep = 0
        st.session_state.user_input = ""
        st.session_state.plan_key_suffix = st.session_state.get("plan_key_suffix", 0) + 1
        st.rerun()
    
    def initial_prompt(self):
        key, prompt_text = self.plan_keys[self.substep]
        suffix = st.session_state.get("plan_key_suffix", 0)
        answer = st.text_input(f"Q{self.substep + 1}: {prompt_text}", key=f"plan_{self.substep}_{suffix}")
        self.next_back_button(answer, prompt_text)

    def output_page(self):
        st.success("All questions answered!")
        self.present_input()
        validity, data = tools.validate_user_input(
                    st.session_state.llm.llm,
                    "backend/schemas/user_input.schema.json",
                    st.session_state.user_input
                )
        if validity:
            travel_info = fetch_all_travel_info(
                data,
                self.hotel,
                self.future_flight,
                self.weather,
                self.attraction_api,
                self.restaurant_api,
            )
            output = tools.generate_plan(
                self.llm.llm,
                st.session_state.user_input,
                data,
                travel_info
            )
            st.write(output)
        else:
            st.error(data)


    def run(self):
        st.title("Generate Complete Plan")
        st.text("Follow the steps to enter basic info + additional requirements for a personalized plan:") 
        self.substep = st.session_state.plan_substep
        if self.substep < self.key_length:
            self.initial_prompt()
        else:
            self.output_page()

        st.markdown("<br><br>", unsafe_allow_html=True)
        cols = st.columns([8, 2])
        with cols[1]:
            if st.button("Reset", use_container_width=True):
                self.reset()