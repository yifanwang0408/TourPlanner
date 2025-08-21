import streamlit as st
from backend.utils import fetch_all_travel_info, fetch_additional_info
import backend.tools as tools
from backend.plan import Plan

class PlanInfo:
    def __init__(self, llm, hotel, future_flight, weather, attraction_api, restaurant_api):

        if "plan_substep" not in st.session_state:
            st.session_state.plan_substep = 0
        if "user_input" not in st.session_state:
            st.session_state.user_input = ""
        if "additional_requirement" not in st.session_state:
            st.session_state.additinoal_requirement = ""
        if "plan" not in st.session_state:
            st.session_state.plan = []
        if "info" not in st.session_state:
            st.session_state.info = []
        if "version" not in st.session_state:
            st.session_state.version = 1

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

    def refine_prompt(self):
        st.write("Any additional requirement to refine the plan?")
        answer = st.text_input("Please enter")
        if st.button("Refine") and answer.strip():
            st.session_state.additinoal_requirement = answer
            st.session_state.plan_substep += 1
            st.rerun()

    def refine(self):
        #refetch check
        original_info = st.session_state.info[0]
        original_input, original_plan = st.session_state.plan[-1].user_input, st.session_state.plan[-1].plan
        print()
        refetch, fields, refetch_json = tools.refetch_check(self.llm.llm, original_info, original_input, st.session_state.additinoal_requirement, original_plan, "backend/schemas/user_input.schema.json")
        if refetch:
            #get additional info
            additional_info = fetch_additional_info(refetch_json, fields, self.hotel,self.future_flight,self.weather,self.attraction_api,self.restaurant_api)
            st.session_state.info.append(additional_info)
            #get the plan
            summary = tools.refine_plan(self.llm.llm, original_plan, st.session_state.additinoal_requirement, additional_info, original_info)
            #create the plan class
            plan = Plan(st.session_state.additinoal_requirement, refetch_json, summary, len(st.session_state.plan)+1)
            st.session_state.plan.append(plan)
            st.session_state.plan_substep = self.key_length
            st.session_state.version += 1
            st.rerun()
        else:
            plan = tools.refine_plan(self.llm.llm, original_plan, st.session_state.additinoal_requirement, {}, original_info)
            st.session_state.plan.append(refetch_json, plan)
            st.session_state.plan_substep = self.key_length
            st.session_state.version += 1
            st.rerun()

    def output_refine(self, version):
        plan = st.session_state.plan[version-1]
        plan.present()

    def initial_prompt(self):
        key, prompt_text = self.plan_keys[self.substep]
        suffix = st.session_state.get("plan_key_suffix", 0)
        answer = st.text_input(f"Q{self.substep + 1}: {prompt_text}", key=f"plan_{self.substep}_{suffix}")
        self.next_back_button(answer, prompt_text)

    def initial_plan(self):
        st.success("All questions answered!")
        placeholder = st.empty() 
        placeholder.markdown("## ⏳ Loading... Please wait")
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
            st.session_state.info.append(travel_info)
            output = tools.generate_plan(
                self.llm.llm,
                st.session_state.user_input,
                data,
                travel_info
            )
            placeholder.empty() 
            plan = Plan(st.session_state.user_input, data, output, 1)
            st.session_state.plan.append(plan)
            plan.present()
        else:
            placeholder.empty() 
            st.error(data)

    def output_page(self):
        print(len(st.session_state.plan))
        if len(st.session_state.plan) == 0:
            version_labels = [f"version {x+1}" for x in range(st.session_state["version"])]

            # Selectbox returns a string label
            st.session_state["selected_version"] = st.selectbox(
                "Choose a version:", version_labels
            )

            # Convert selected label back to an integer index
            selected_version = int(st.session_state["selected_version"].split()[-1])
            self.initial_plan()
            self.refine_prompt()
        else:
            version_labels = [f"version {x+1}" for x in range(st.session_state["version"])]

            # Selectbox returns a string label
            st.session_state["selected_version"] = st.selectbox(
                "Choose a version:", version_labels
            )

            # Convert selected label back to an integer index
            selected_version = int(st.session_state["selected_version"].split()[-1])
            self.output_refine(selected_version)
            self.refine_prompt()
        



    def run(self):
        st.title("Generate Complete Plan")
        st.text("Follow the steps to enter basic info + additional requirements for a personalized plan:") 
        self.substep = st.session_state.plan_substep
        if self.substep < self.key_length:
            self.initial_prompt()
        elif self.substep == self.key_length + 1:
            self.refine()
        else:
            self.output_page()

        st.markdown("<br><br>", unsafe_allow_html=True)
        cols = st.columns([8, 2])
        with cols[1]:
            if st.button("Reset", use_container_width=True):
                self.reset()
