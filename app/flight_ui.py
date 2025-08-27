import streamlit as st

import backend.tools as tools
from backend.travel_api import FutureFlight_Aviationstack
from backend.utils import future_flight_input_prompt

class FlightInfo:
    def __init__(self, llm):
        #set up api to fetch info
        if "future_flight" not in st.session_state:
            st.session_state.future_flight = FutureFlight_Aviationstack("Future Flight Schedules (Aviationstack)")
            
        #flight variable setup
        if "flight_params" not in st.session_state:
            st.session_state.flight_params = {}
        if "flight_substep" not in st.session_state:
            st.session_state.flight_substep = 0
        if "flight_invalid_fields" not in st.session_state:
            st.session_state.flight_invalid_fields = []
        if "flight_preference" not in st.session_state:
            st.session_state.flight_preference = ""
            
        self.substep = st.session_state.flight_substep
        self.future_flight = st.session_state.future_flight
        self.keys = ["airport_dep", "airport_arr", "date_dep", "date_arr"]
        self.llm = llm
        self.keys_length = len(self.keys)
        
    @staticmethod
    def next_back_button(answer, key): 
        cols = st.columns(9)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.flight_substep > 0:
                st.session_state.flight_substep -= 1
                st.rerun()

        with cols[8]:
            if st.button("Next") and answer.strip():
                st.session_state.flight_params[key] = answer
                st.session_state.flight_substep += 1
                st.rerun()
                
    def reset(self):
        st.session_state.flight_substep = 0
        st.session_state.flight_params = {}
        st.session_state.flight_invalid_fields = []
        
        st.session_state.flight_key_suffix = st.session_state.get("flight_key_suffix", 0) + 1
        
        st.rerun()
        
    def present_input(self):
        st.write("Your Input:")
        for key in self.keys:
            st.write(f"{future_flight_input_prompt[key]} {st.session_state.flight_params[key]}")
        st.markdown("\n---\n")
                
    def initial_prompt(self):
        key = self.keys[self.substep]
        st.write(f"Q{self.substep + 1}: {future_flight_input_prompt[key]}")
        #answer = st.text_input("Please Enter:", key=f"flight_{self.substep}")
        suffix = st.session_state.get("flight_key_suffix", 0)
        answer = st.text_input("Please Enter:", key=f"flight_{self.substep}_{suffix}")

        self.next_back_button(answer, key)

    def preference_page(self):
        st.write(f"Do you have any preference on flight?")
        answer = st.text_input("Please Enter: ")
        cols = st.columns(9)  
        
        with cols[0]:
            if st.button("Back") and st.session_state.flight_substep > 0:
                st.session_state.flight_substep -= 1
                st.rerun()
        with cols[8]:
            if st.button("Next"):
                st.session_state.flight_substep += 1
                st.session_state.flight_preference = answer
                st.rerun()

    def output_page(self):
        # All questions answered
        st.success("All questions answered!")
        self.present_input()
        placeholder = st.empty() 
        placeholder.markdown("## ⏳ Loading... Please wait")
        validity, message, st.session_state.flight_invalid_fields = tools.validate_user_input_single_api_call_app(self.llm.llm, "flight", st.session_state.flight_params)
        if validity == True:
            travel_info = self.future_flight.get_future_flight_schedules(st.session_state.flight_params)
            summary = tools.generate_travel_info_search_summary(self.llm.llm, "flight", travel_info, st.session_state.flight_params)
            placeholder.empty()
            st.write(summary)
            st.caption("The information is powered by aviationstack.")
        else:
            placeholder.empty() 
            st.write(message)
            st.write("Do you want to re-enter these field?")
            cols = st.columns(9)  # create 2 columns
            with cols[0]:
                if st.button("No"):
                    self.reset()
            with cols[8]:
                if st.button("Yes"):
                    st.session_state.flight_substep += 1
                    st.rerun()

        
    def reprompt(self):
        if self.substep < len(self.keys) + len(st.session_state.flight_invalid_fields) + 2:
            key = st.session_state.flight_invalid_fields[self.substep-(self.keys_length+2)]
            st.write(f"Q{self.substep + 1}: {future_flight_input_prompt[key]}")
            answer = st.text_input("Please Enter:", key=f"flight_{self.substep}")

            self.next_back_button(answer, key)
            
        else:
            st.session_state.flight_substep =  self.keys_length+1
            st.rerun()

    def run(self):
        st.title("Get Future Flight Schedules")
        st.text("Follow the steps to fetch future flight schedules")
        self.substep = st.session_state.flight_substep
        if self.substep <  self.keys_length:
            self.initial_prompt()
        elif self.substep ==  self.keys_length:
            self.preference_page()
        elif self.substep == self.keys_length + 1:
            self.output_page()
        else:
            self.reprompt()
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        cols = st.columns([8, 2])
        with cols[1]:
            if st.button("Reset", use_container_width=True):
                self.reset()