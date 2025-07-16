import json
from llm import LLM
import tools


if __name__ == "__main__":


    llm = LLM("open-api-key", "llm-tourplanner")
    llm.get_api_key()
    llm.setup()
    
    #for testing user input
    user_input = input("input your travel plan and preference: ")
    #user input schema
    input_schema = "schemas/user_input_test.schema.json"
    #call for validation
    validity, message = tools.validate_user_input(llm.llm, input_schema, user_input)

    print(message)







