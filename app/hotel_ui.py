import streamlit as st

import backend.tools as tools
from backend.travel_api import Hotel_LiteAPI
from backend.utils import hotel_input_prompt


class HotelInfo:
    def __init__(self, llm):
        #set up api to fetch info
        if "hotel_lite" not in st.session_state:
            st.session_state.hotel_lite = Hotel_LiteAPI("Hotel Lite API","https://api.liteapi.travel")
        #hotel variable setup
        if "hotel_params" not in st.session_state:
            st.session_state.hotel_params={}
        if "hotel_substep" not in st.session_state:
            st.session_state.hotel_substep = 0
        if "hotel_invalid_fields" not in st.session_state:
            st.session_state.hotel_invalid_fields = []
        self.substep = st.session_state.hotel_substep
        self.hotel_lite = st.session_state.hotel_lite
        self.keys = ["city", "countryCode", "minRating", "starRating"]
        self.llm = llm
        self.keys_length = len(self.keys)
    
    @staticmethod
    def next_back_button(answer, key): 
        cols = st.columns(9)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.hotel_substep > 0:
                st.session_state.hotel_substep -= 1
                st.rerun()

        with cols[8]:
            if st.button("Next") and answer.strip():
                st.session_state.hotel_params[key] = answer
                st.session_state.hotel_substep += 1
                st.rerun()
                
    def reset(self):
        st.session_state.hotel_substep = 0
        st.session_state.hotel_params = {}
        st.session_state.hotel_invalid_fields = []
        st.session_state.hotel_key_suffix = st.session_state.get("hotel_key_suffix", 0) + 1
        st.rerun()
        
    def present_input(self):
        st.write("Your Input:")
        for key in self.keys:
            st.write(f"{hotel_input_prompt[key]} {st.session_state.hotel_params[key]}")
        st.markdown("\n---\n")
                
    def initial_prompt(self):
        key = self.keys[self.substep]
        st.write(f"Q{self.substep + 1}: {hotel_input_prompt[key]}")
        #answer = st.text_input("Please Enter:", key=f"hotel_{self.substep}")
        suffix = st.session_state.get("hotel_key_suffix", 0)
        answer = st.text_input("Please Enter:", key=f"hotel_{self.substep}_{suffix}")
        self.next_back_button(answer, key)

    def output_page(self):
        # All questions answered
        st.success("All questions answered!")
        self.present_input()
        placeholder = st.empty() 
        placeholder.markdown("## ⏳ Loading... Please wait")
        st.session_state.hotel_params["limit"] = 5
        validity, message, st.session_state.hotel_invalid_fields = tools.validate_user_input_single_api_call_app(self.llm.llm, "hotel", st.session_state.hotel_params)
        if validity == True:
            travel_info = self.hotel_lite.get_hotel_list(url="https://api.liteapi.travel/v3.0/data/hotels",params=st.session_state.hotel_params)
            summary = tools.generate_travel_info_search_summary(self.llm.llm, "hotel", travel_info, st.session_state.hotel_params)
            placeholder.empty()
            st.write(summary)
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
                    st.session_state.hotel_substep += 1
                    st.rerun()
        
    def reprompt(self):
        if self.substep < self.keys_length + len(st.session_state.hotel_invalid_fields) + 1:
            key = st.session_state.hotel_invalid_fields[self.substep-( self.keys_length+1)]
            st.write(f"Q{self.substep + 1}: {hotel_input_prompt[key]}")
            answer = st.text_input("Please Enter:", key=f"hotel_{self.substep}")

            self.next_back_button(answer, key)
            
        else:
            st.session_state.hotel_substep =  self.keys_length
            st.rerun()

    def run(self):
        st.title("Get Hotel")
        st.text("Follow the steps to fetch hotel information")
        self.substep = st.session_state.hotel_substep
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