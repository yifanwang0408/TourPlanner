from langchain.tools import tool
from prompt import prompt1
import json
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate


def validate_user_input(llm, input_schema, user_input):
    """parse user input and validate it, return the parsed input if it is valid
    
    Args:
        llm: the llm connection
        user_input: the user input
        input_schema: the schema of the input

    Return:
        A True if the user input along with parsed data if user input is valid, or a False with error message if invalid.
    """

    with open(input_schema, "r") as f:
        schema_str = json.load(f)
    
    #system prompt
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt1)
    #user prompt
    user_prompt_template = HumanMessagePromptTemplate.from_template("{user_input}")

    prompt = ChatPromptTemplate.from_messages([
        system_prompt_template, 
        user_prompt_template
    ])
    
    chain = (
        {   "schema_str": lambda x: x["schema_str"],
            "user_input": lambda x: x["user_input"]
        } 
        | prompt 
        | llm
        | {"response": lambda x: json.loads(x.content)} #because prompt1 ask it to direcly only output in json
    )
    response = chain.invoke({"schema_str": schema_str, "user_input": user_input})
    
    parsed_input = response["response"]

    if parsed_input["data"] is None:
        return False, parsed_input["message"]
    else:
        return True, parsed_input["data"]


    

    
    
