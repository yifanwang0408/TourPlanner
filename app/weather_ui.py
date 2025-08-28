import streamlit as st

from backend import tools
from backend.travel_api import Weather_WeatherAPI
from backend.utils import weather_input_prompt


class WeatherInfo:
    def __init__(self, llm):
        #set up api to fetch info
        if "weather" not in st.session_state:
            st.session_state.weather = Weather_WeatherAPI("Weather Forecast")
            
        #weather forecast setup
        if "weather_params" not in st.session_state:
            st.session_state.weather_params = {}
        if "weather_substep" not in st.session_state:
            st.session_state.weather_substep = 0
        if "weather_invalid_fields" not in st.session_state:
            st.session_state.weather_invalid_fields = []
        if "weather_summary_stored" not in st.session_state:
            st.session_state.weather_summary_stored = {}
            
        self.substep = st.session_state.weather_substep
        self.weather = st.session_state.weather
        self.keys = ["city", "date"]
        self.llm = llm
        self.keys_length = len(self.keys)
    
    @staticmethod
    def next_back_button(answer, key): 
        cols = st.columns(9)  # create 2 columns

        with cols[0]:
            if st.button("Back") and st.session_state.weather_substep > 0:
                st.session_state.weather_substep -= 1
                st.rerun()

        with cols[8]:
            if st.button("Next") and answer.strip():
                st.session_state.weather_params[key] = answer
                st.session_state.weather_substep += 1
                st.rerun()
                
                
    def reset(self):
        st.session_state.weather_substep = 0
        st.session_state.weather_params = {}
        st.session_state.weather_invalid_fields = []
        st.session_state.weather_key_suffix = st.session_state.get("weather_key_suffix", 0) + 1
        st.rerun()
                
    def initial_prompt(self):
        key = self.keys[self.substep]
        st.write(f"Q{self.substep + 1}: {weather_input_prompt[key]}")
        #answer = st.text_input("Please Enter:", key=f"hotel_{self.substep}")
        suffix = st.session_state.get("weather_key_suffix", 0)
        answer = st.text_input("Please Enter:", key=f"weather_{self.substep}_{suffix}")
        self.next_back_button(answer, key)
        
    def present_input(self):
        st.write("Your Input:")
        for key in self.keys:
            st.write(f"{weather_input_prompt[key]} {st.session_state.weather_params[key]}")
        st.markdown("\n---\n")
        
    def output_page(self):
        # All questions answered
        st.success("All questions answered!")
        self.present_input()
        placeholder = st.empty() 
        placeholder.markdown("## ⏳ Loading... Please wait")
        if str(st.session_state.weather_params) in st.session_state.weather_summary_stored.keys():
            placeholder.empty()
            st.write(st.session_state.weather_summary_stored[str(st.session_state.weather_params)])
            st.caption("The information is powered by OpenWeatherMap.")
        else:
            validity, message, st.session_state.weather_invalid_fields = tools.validate_user_input_single_api_call_app(self.llm.llm, "weather", st.session_state.weather_params)
            if validity == True:
                travel_info = self.weather.get_forecast(st.session_state.weather_params)
                summary = tools.generate_travel_info_search_summary(self.llm.llm, "weather", travel_info, st.session_state.weather_params)
                placeholder.empty()
                st.write(summary)
                st.session_state.weather_summary_stored[str(st.session_state.weather_params)] = summary
                st.caption("The information is powered by OpenWeatherMap.")
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
                        st.session_state.weather_substep += 1
                        st.rerun()
                    
    def reprompt(self):
        if self.substep < self.keys_length + len(st.session_state.weather_invalid_fields) + 1:
            key = st.session_state.weather_invalid_fields[self.substep-( self.keys_length+1)]
            st.write(f"Q{self.substep + 1}: {weather_input_prompt[key]}")
            answer = st.text_input("Please Enter:", key=f"weather_{self.substep}")

            self.next_back_button(answer, key)
            
        else:
            st.session_state.weather_substep =  self.keys_length
            st.rerun()

    def run(self):
        st.title("Get Weather")
        st.text("Follow the stseps to fetch weather information")
        self.substep = st.session_state.weather_substep
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