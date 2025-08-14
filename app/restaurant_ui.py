import streamlit as st
from backend.utils import transfer_interest_id, restaurant_prompt
import backend.tools as tools
from backend.places_category_id import restaurant_categories_str, restaurant_categories
from backend.travel_api import Restaurant_API


class RestaurantInfo:
    def __init__(self, llm):
        #set up api to fetch info
        if "restaurant_api" not in st.session_state:
            st.session_state.restaurant_api = Restaurant_API("Restaurant API")
        #restaurant setup
        if "restaurant_params" not in st.session_state:
            st.session_state.restaurant_params = {}
        if "restaurant_substep" not in st.session_state:
            st.session_state.restaurant_substep = 0
            
        self.substep = st.session_state.restaurant_substep
        self.restaurant_api = st.session_state.restaurant_api
        self.keys = ["city", "additional_info", "food_preference"]
        self.llm = llm
        self.keys_length = len(self.keys)
        
    def next_back_button(self, answer, key): 
        cols = st.columns(9)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.restaurant_substep > 0:
                st.session_state.restaurant_substep -= 1
                st.rerun()

        with cols[8]:
            if st.button("Next") and answer.strip():
                if key == "food_preference":
                    interests = tools.categorize_user_input(self.llm.llm, answer, restaurant_categories_str)
                    st.session_state.restaurant_params["fsq_category_ids"] = transfer_interest_id(interests["categories"], restaurant_categories)
                    st.session_state.restaurant_params[key] = answer
                else:
                    st.session_state.restaurant_params[key] = answer
                st.session_state.restaurant_substep += 1
                st.rerun()
                
    def reset(self):
        st.session_state.restaurant_substep = 0
        st.session_state.restaurant_params = {}
        st.session_state.restaurant_key_suffix = st.session_state.get("restaurant_key_suffix", 0) + 1
        st.rerun()
        
    def present_input(self):
        st.write("Your Input:")
        for key in self.keys:
            st.write(f"{restaurant_prompt[key]} {st.session_state.restaurant_params[key]}")
        st.markdown("\n---\n")
                
    def initial_prompt(self):
        key = self.keys[self.substep]
        st.write(f"Q{self.substep + 1}: {restaurant_prompt[key]}")
        #answer = st.text_input("Please Enter:", key=f"restaurant_{self.substep}")
        suffix = st.session_state.get("restaurant_key_suffix", 0)
        answer = st.text_input("Please Enter:", key=f"restaurant_{self.substep}_{suffix}")
        self.next_back_button(answer, key)
        
    def output_page(self):
        # All questions answered
        st.success("All questions answered!")
        self.present_input()
        response  = tools.city_to_latlon(self.llm.llm, st.session_state.restaurant_params["city"], st.session_state.restaurant_params["additional_info"])
        st.session_state.restaurant_params["ll"] = response["ll"]
        st.session_state.restaurant_params["radius"] = response["radius"]
        travel_info = self.restaurant_api.get_restaurant(st.session_state.restaurant_params, limit=10)
        summary = tools.generate_travel_info_search_summary(self.llm.llm, "restaurant", travel_info, st.session_state.restaurant_params)
        st.write(summary)
        if st.button("Restart"):
            self.reset()
    
    def run(self):
        st.title("Get Restaurants")
        st.text("Follow the steps to fetch restaurants")
        self.substep = st.session_state.restaurant_substep
        if self.substep <  self.keys_length:
            self.initial_prompt()
        else:
            self.output_page()
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        cols = st.columns([8, 2])
        with cols[1]:
            if st.button("Reset", use_container_width=True):
                self.reset()