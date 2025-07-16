import json
from llm import LLM
import tools


if __name__ == "__main__":


    llm = LLM("open-api-key", "llm-tourplanner")
    llm.get_api_key()
    llm.setup()
    
    validity = False
    #user input schema
    input_schema = "schemas/user_input_test.schema.json"
    #user input string
    user_input = ""

    while (validity == False):
        #for testing user input
        user_input = user_input + input("input your travel plan and preference: ")
        #call for validation
        validity, message = tools.validate_user_input(llm.llm, input_schema, user_input)

        print(message)
    print("user input valid")







