import streamlit as st

class Plan:
    def __init__(self, user_input, parsed_schema, generated_plan, plan_version):
        self.user_input = user_input
        self.parsed_schema = parsed_schema
        self.plan = generated_plan
        self.version = plan_version

    def __eq__(self, other):
        if not isinstance(other, Plan):
            return False
        return (
            self.user_input == other.user_input and
            self.parsed_schema == other.parsed_schema and
            self.plan == other.plan
        )

    def __str__(self):
        print(f"plan version: {self.version}")

    def present(self):
        st.markdown(f"## Version: {self.version}")
        st.write(self.plan)
        st.markdown("\n---\n")
    
