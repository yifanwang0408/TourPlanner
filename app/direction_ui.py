import streamlit as st

import backend.tools as tools
from backend.travel_api import Directions_OpenRouteService
from backend.utils import direction_input_prompt

class DirectionInfo:
    def __init__(self, llm):
        #set up api to fetch info
        if "direction" not in st.session_state:
            st.session_state.direction = Directions_OpenRouteService("Directions (OpenRouteService)")
        #direction setup
        if "direction_params" not in st.session_state:
            st.session_state.direction_params = {}
        if "direction_substep" not in st.session_state:
            st.session_state.direction_substep = 0
        if "direction_invalid_fields" not in st.session_state:
            st.session_state.direction_invalid_fields = []
            
        self.substep = st.session_state.direction_substep
        self.direction = st.session_state.direction
        self.keys = ["start_lon", "start_lat", "end_lon", "end_lat"]
        self.llm = llm
        self.keys_length = len(self.keys)
    
    @staticmethod
    def next_back_button(answer, key): 
        cols = st.columns(9)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.direction_substep > 0:
                st.session_state.direction_substep -= 1
                st.rerun()

        with cols[8]:
            if st.button("Next") and answer.strip():
                st.session_state.direction_params[key] = answer
                st.session_state.direction_substep += 1
                st.rerun()
                
    def reset(self):
        st.session_state.direction_substep = 0
        st.session_state.direction_params = {}
        st.session_state.direction_invalid_fields = []
        st.session_state.direction_key_suffix = st.session_state.get("direction_key_suffix", 0) + 1
        st.rerun()
    
    def present_input(self):
        st.write("Your Input:")
        for key in self.keys:
            st.write(f"{direction_input_prompt[key]} {st.session_state.direction_params[key]}")
        st.markdown("\n---\n")
            
    def initial_prompt(self):
        key = self.keys[self.substep]
        st.write(f"Q{self.substep + 1}: {direction_input_prompt[key]}")
        #answer = st.text_input("Please Enter:", key=f"direction_{self.substep}")
        suffix = st.session_state.get("direction_key_suffix", 0)
        answer = st.text_input("Please Enter:", key=f"direction_{self.substep}_{suffix}")
        self.next_back_button(answer, key)
        
    def output_page(self):
        # All questions answered
        st.success("All questions answered!")
        self.present_input()
        validity, message, st.session_state.direction_invalid_fields =  tools.validate_user_input_single_api_call_app(self.llm.llm, "direction", st.session_state.direction_params)
        if validity == True:
            travel_info = self.direction.get_directions(st.session_state.direction_params)
            summary = tools.generate_travel_info_search_summary(self.llm.llm, "direction", travel_info, st.session_state.direction_params)
            st.write(summary)
            if st.button("Restart"):
                        st.session_state.direction_substep = 0
                        st.session_state.direction_params = {}
                        st.session_state.direction_invalid_fields = []
                        st.rerun()
        else:
            st.write(message)
            st.write("Do you want to re-enter these field?")
            cols = st.columns(4)  # create 2 columns
            with cols[0]:
                if st.button("No"):
                    if st.button("Restart"):
                        self.reset()
                        
            with cols[3]:
                if st.button("Yes"):
                    st.session_state.direction_substep += 1
                    st.rerun()
    
    def reprompt(self):
        if self.substep < self.keys_length + len(st.session_state.direction_invalid_fields) + 1:
            key = st.session_state.direction_invalid_fields[self.substep-( self.keys_length+1)]
            st.write(f"Q{self.substep + 1}: {direction_input_prompt[key]}")
            answer = st.text_input("Please Enter:", key=f"direction_{self.substep}")

            self.next_back_button(answer, key)
            
        else:
            st.session_state.direction_substep =  self.keys_length
            st.rerun()
    
    def run(self):
        st.title("Get Directions")
        st.text("Follow the steps to fetch Directions")
        self.substep = st.session_state.direction_substep
        if self.substep <  self.keys_length:
            self.initial_prompt()
        elif self.substep ==  self.keys_length:
            self.output_page()
        else:
            self.reprompt()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        cols = st.columns([8, 2])
        with cols[1]:
            if st.button("Reset", use_container_width=True):
                self.reset()