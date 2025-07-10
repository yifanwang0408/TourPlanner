from langchain.tools import tool
from prompt import prompt1
import json
from langchain.prompts import PromptTemplate

@tool
def validate_user_input(llm, input_schema, user_input):
    """parse user input and validate it, return the parsed input if it is valid
    
    Args:
        llm: the llm connection
        user_input: the user input
        input_schema: the schema of the input

    Return:
        A string indicating 'valid' or 'invalid' along with parsed data or error message.
    """

    schema_str = json.dumps(input_schema, indent=2)
    system_prompt_template = PromptTemplate(
        input_variables=["schema_str"],
        template =  prompt1
    )

    message = [
        {
            "role": "system",
            "content": system_prompt_template.format(schema_str=schema_str)
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    response = llm(message)
    content = response["choice"][0]["message"]["content"]
    parsed_input = json.loads(content)
    if parsed_input["data"] is None:
        return "invalid", parsed_input["message"]
    return "valid", parsed_input["data"]

    
    
