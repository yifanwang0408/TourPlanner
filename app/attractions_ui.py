import streamlit as st

import backend.tools as tools
from backend.travel_api import Attractions_API
from backend.utils import site_visit_prompt, transfer_interest_id

from backend.places_category_id import site_categories, site_categories_str


class AttractionInfo:
    def __init__(self, llm):
        #set up api to fetch info
        if "attraction_api" not in st.session_state:
            st.session_state.attraction_api = Attractions_API("Attractions API")
        #attraction setup
        if "attraction_params" not in st.session_state:
            st.session_state.attraction_params = {}
        if "attraction_substep" not in st.session_state:
            st.session_state.attraction_substep = 0
        if "attraction_preference" not in st.session_state:
            st.session_state.attraction_preference = ""
        if "attraction_summary_stored" not in st.session_state:
            st.session_state.attraction_summary_stored = {}
            
        self.substep = st.session_state.attraction_substep
        self.attraction_api = st.session_state.attraction_api
        self.keys = ["city", "additional_info", "interest"]
        self.llm = llm
        self.keys_length = len(self.keys)
        
    
    def next_back_button(self, answer, key): 
        cols = st.columns(9)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.attraction_substep > 0:
                st.session_state.attraction_substep -= 1
                st.rerun()

        with cols[8]:
            if st.button("Next") and answer.strip():
                if key == "interest":
                    interests = tools.categorize_user_input(self.llm.llm, answer, site_categories_str)
                    st.session_state.attraction_params["category"] = transfer_interest_id(interests["categories"],site_categories)
                    st.session_state.attraction_params[key] = answer
                else:
                    st.session_state.attraction_params[key] = answer
                st.session_state.attraction_substep += 1
                st.rerun()
                
    def reset(self):
        st.session_state.attraction_substep = 0
        st.session_state.attraction_params = {}
        st.session_state.attraction_preference = ""
        
        st.session_state.attraction_key_suffix = st.session_state.get("attraction_key_suffix", 0) + 1
        
        st.rerun()
    
    def present_input(self):
        st.write("Your Input:")
        for key in self.keys:
            st.write(f"{site_visit_prompt[key]} {st.session_state.attraction_params[key]}")
        
                
    def initial_prompt(self):
        key = self.keys[self.substep]
        st.write(f"Q{self.substep + 1}: {site_visit_prompt[key]}")
        #answer = st.text_input("Please Enter:", key=f"attraction_{self.substep}")
        suffix = st.session_state.get("attraction_key_suffix", 0)
        answer = st.text_input("Please Enter:", key=f"attraction_{self.substep}_{suffix}")
        self.next_back_button(answer, key)

    def preference_page(self):
        st.write(f"Do you have any preference on attractions to visit?")
        answer = st.text_input("Please Enter: ")
        cols = st.columns(9)  
        
        with cols[0]:
            if st.button("Back") and st.session_state.attraction_substep > 0:
                st.session_state.attraction_substep -= 1
                st.rerun()
        with cols[8]:
            if st.button("Next"):
                st.session_state.attraction_substep += 1
                st.session_state.attraction_preference = answer
                st.rerun()

    def output_page(self):
        # All questions answered
        st.success("All questions answered!")
        self.present_input()
        placeholder = st.empty() 
        placeholder.markdown("## ⏳ Loading... Please wait")
        if str(st.session_state.attraction_params) in st.session_state.attraction_summary_stored.keys():
            placeholder.empty()
            st.write(st.session_state.attraction_summary_stored[str(st.session_state.attraction_params)])
        else:
            response  = tools.city_to_latlon(self.llm.llm, st.session_state.attraction_params["city"], st.session_state.attraction_params["additional_info"])
            st.session_state.attraction_params["ll"] = response["ll"]
            st.session_state.attraction_params["radius"] = response["radius"]
            travel_info = self.attraction_api.get_attractions(st.session_state.attraction_params, limit=10)
            summary = tools.generate_travel_info_search_summary(self.llm.llm, "site", travel_info, st.session_state.attraction_params, st.session_state.attraction_preference)
            placeholder.empty()
            st.write(summary)
            st.session_state.attraction_summary_stored[str(st.session_state.attraction_params)] = summary
        st.caption("The information is powered by FOURSQUARE.")
    

    
    def run(self):
        st.title("Get Attractions")
        st.text("Follow the steps to fetch attractions")
        self.substep = st.session_state.attraction_substep
        if self.substep <  self.keys_length:
            self.initial_prompt()
        elif self.substep == self.keys_length:
            self.preference_page()
        else:
            self.output_page()
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        cols = st.columns([8, 2])
        with cols[1]:
            if st.button("Reset", use_container_width=True):
                self.reset()
