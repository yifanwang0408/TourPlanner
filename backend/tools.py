from langchain.tools import tool
from prompt import prompt1, prompt2, prompt3, prompt4
import json
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from datetime import date
from llm import LLM

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
    
    
    today_str = date.today().isoformat()
    
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
            "today_str": lambda x: x["today_str"],
            "user_input": lambda x: x["user_input"]
        } 
        | prompt 
        | llm
        | {"response": lambda x: x.content} #because prompt1 ask it to direcly only output in json
    )
    response = chain.invoke({"schema_str": schema_str, "today_str": today_str,"user_input": user_input})
    parsed_input = json.loads(response["response"])

    if parsed_input["data"] is None:
        return False, parsed_input["message"]
    else:
        return True, parsed_input["data"]
    

def generate_plan(llm: LLM, user_input: str, parsed_input: dict, travel_info: dict) -> str:
    """
    The function call LLM with collected travel_info and user input to generate a plan for user

    Args:
        llm: the llm connection
        user_input: the user input
        parsed_input: dictionary of parsed user input
        travel_info: collected travel information

    Return:
        the generated plan for user
    """

    #system prompt
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt2)
    #user prompt
    user_prompt_template = HumanMessagePromptTemplate.from_template("{user_input}")

    prompt = ChatPromptTemplate.from_messages([
        system_prompt_template, 
        user_prompt_template
    ])
    
    chain = (
        {   "parsed_input": lambda x: x["parsed_input"],
            "travel_info": lambda x: x["travel_info"],
            "user_input": lambda x: x["user_input"]
        } 
        | prompt 
        | llm
        | {"response": lambda x: x.content} 
    )
    response = chain.invoke({"parsed_input": parsed_input, "travel_info": travel_info,"user_input": user_input})
    
    output = response["response"]
    return output

def validate_user_input_single_api_call(llm: LLM, travel_info_category: str, user_input: dict) -> str:
    """
    The function validate user input for single api call (for choice 1-4)

    Args:
        llm: the llm connectino
        travel_info_category: the category of the travel information
        user_input: user input

    Return:
        (validition(bool), message(str), invalid_fields)
    """
    #system prompt
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt4)
    #user prompt
    user_prompt_template = HumanMessagePromptTemplate.from_template("Validate user input")

    prompt = ChatPromptTemplate.from_messages([
        system_prompt_template, 
        user_prompt_template
    ])

    chain = (
        {   "travel_info_category": lambda x: x["travel_info_category"],
            "user_input": lambda x: x["user_input"],
        } 
        | prompt 
        | llm
        | {"response": lambda x: x.content} #because prompt1 ask it to direcly only output in json
    )
    response = chain.invoke({"travel_info_category": travel_info_category, "user_input": user_input})
    print(response)
    output = json.loads(response["response"])

    validity = output["validity"]
    message = output["message"]
    invalid_fields = output["invalid_fields"]
    return validity, message, invalid_fields


def generate_travel_info_search_summary(llm: LLM, travel_info_category: str, search_info: dict, user_input: dict) -> str:
    """
    The function generate a summary on the travel information search

    Args:
        llm: the llm connection
        travel_info_category: the category of travel information
        search_info: the info fetched from api
        user_input: the user input (parameters)

    Return:
        return the searh info summary
    """
    #system prompt
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt3)
    #user prompt
    user_prompt_template = HumanMessagePromptTemplate.from_template("{user_input}")

    prompt = ChatPromptTemplate.from_messages([
        system_prompt_template, 
        user_prompt_template
    ])
    
    chain = (
        {   "travel_component": lambda x: x["travel_component"],
            "info_json": lambda x: x["info_json"],
            "user_input": lambda x: x["user_input"]
        } 
        | prompt 
        | llm
        | {"response": lambda x: x.content} #because prompt1 ask it to direcly only output in json
    )
    response = chain.invoke({"travel_component": travel_info_category, "info_json": search_info,"user_input": user_input})
    
    output = response["response"]
    return output

    
    
