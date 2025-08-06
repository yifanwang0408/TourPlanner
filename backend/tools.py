from langchain.tools import tool
from prompt import prompt1, prompt2, prompt3, prompt4, prompt5, prompt6, prompt_parsing_output
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

    
    
def city_to_latlon(llm: LLM, city_name:str, additional_info:str)->dict:
    """
    The functino take city as input and output
    """
    #system prompt
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt5)
    #user prompt
    #user_prompt_template = HumanMessagePromptTemplate.from_template("{user_input}")

    prompt = ChatPromptTemplate.from_messages([
        system_prompt_template, 
        #user_prompt_template
    ])
    
    chain = (
        {   "city_name": lambda x: x["city_name"],
            "additional_info": lambda x: x["additional_info"],
            #"user_input": lambda x: x["user_input"]
        } 
        | prompt 
        | llm
        | {"response": lambda x: x.content} #because prompt1 ask it to direcly only output in json
    )
    response = chain.invoke({"city_name": city_name, "additional_info": additional_info})
    output = json.loads(response["response"])
    return output



def categorize_user_input(llm: LLM, user_input:str, categories_str: str)->list:
    """
    This function take user input on interest

    Args:
        llm: llm connection
        user_input: string on user interest

    Return:
        a list of interest categories,
    """
    #system prompt
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt6)
    #user prompt
    user_prompt_template = HumanMessagePromptTemplate.from_template("{user_input}")

    prompt = ChatPromptTemplate.from_messages([
        system_prompt_template, 
        user_prompt_template
    ])
    
    chain = (
        {  
            "interest_categories": lambda x: x["interest_categories"],
            "user_input": lambda x: x["user_input"]
        } 
        | prompt 
        | llm
        | {"response": lambda x: x.content} #because prompt1 ask it to direcly only output in json
    )
    response = chain.invoke({"interest_categories": categories_str,"user_input": user_input})
    output = json.loads(response["response"])
    return output


def generate_plan_json(llm: LLM, output_schema: str, plan: str) -> str:
    """
    The function call LLM to parse the plan into json format

    Args:
        llm: the llm connection
        output_schema: the path to the output schema
        plan: the tour plan
        

    Return:
        the json format of the generated plan for user
    """

    with open(output_schema, "r") as f:
        schema_str = json.load(f)

    #system prompt
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt_parsing_output)

    prompt = ChatPromptTemplate.from_messages([
        system_prompt_template, 
    ])
    
    chain = (
        {   "output_schema": lambda x: x["output_schema"],
            "plan": lambda x: x["plan"],
        } 
        | prompt 
        | llm
        | {"response": lambda x: x.content} 
    )
    response = chain.invoke({"output_schema": schema_str, "plan": plan})
    output = response["response"]
    output = json.loads(output)
    return output


def reprompt_invalid_fields(params: dict, invalid_fields: list) -> dict:
    for field in invalid_fields:
        print(f"⚠️ Invalid input for '{field}'. Please re-enter:")
        new_val = input(f"{field}: ").strip()
        # Convert numeric inputs when appropriate
        if new_val.isdigit():
            new_val = int(new_val)
        elif new_val.replace(".", "", 1).isdigit():
            new_val = float(new_val)
        params[field] = new_val
    return params

def validate_user_input_single_api_call(llm: LLM, travel_info_category: str, user_input: dict):
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt4)
    user_prompt_template = HumanMessagePromptTemplate.from_template("Validate user input")
    prompt = ChatPromptTemplate.from_messages([system_prompt_template, user_prompt_template])

    while True:
        chain = (
            {
                "travel_info_category": lambda x: x["travel_info_category"],
                "user_input": lambda x: x["user_input"],
            }
            | prompt
            | llm
            | {"response": lambda x: x.content}
        )
        response = chain.invoke({
            "travel_info_category": travel_info_category,
            "user_input": user_input
        })
        print(response)
        output = json.loads(response["response"])
        if output["validity"]:
            return True, "✅ All fields valid.", []
        else:
            print(f"\n🚫 {output['message']}")
            invalid_fields = output["invalid_fields"]
            user_input = reprompt_invalid_fields(user_input, invalid_fields)
