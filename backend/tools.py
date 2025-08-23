from langchain.tools import tool
from prompts import prompt1, prompt2, prompt3, prompt4, prompt5, prompt6, prompt_parsing_output,prompt_determine_refetch,prompt_inprove
import json
from datetime import date

from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)
from langchain.tools import tool
from llm import LLM

prompt_validation ={
    "weather": "1. The city must be a real city.\n2. The date must be a valid calendar date.",
    "direction": "1. The start_longitude, start_latitude, end_longitude, and end_latitude must be within valid Earth coordinate ranges",
    "hotel": "1. The city must be a real city.\n2. The countryCode must exist and match the city.\n3. The min_rating must be between 0 and 10 inclusive (accept numbers like 6, 6.0).  Important!!!Integers, float, and strings representing numbers are accepted.\n4. The starRating must be between 1 and 5 inclusive, with allowed decimals '.0' or '.5' (e.g., 3.5, 4.0, 5.0, 4, 5). Important!!!Integers, float, and strings representing numbers are accepted.\n",
    "flight": "1. The airport IATA code ('airport_dep' and 'airport_arr' field) must exist.\n2. The date ('date_dep' and 'date_arr') must be a valid calendar date."
}
def validate_user_input(llm, input_schema, user_input):
    with open(input_schema, "r") as f:
        schema_str = json.load(f)
    
    today_str = date.today().isoformat()
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt1)
    user_prompt_template = HumanMessagePromptTemplate.from_template("{user_input}")
    prompt = ChatPromptTemplate.from_messages([system_prompt_template, user_prompt_template])

    chain = (
        {
            "schema_str": lambda x: x["schema_str"],
            "today_str": lambda x: x["today_str"],
            "user_input": lambda x: x["user_input"]
        }
        | prompt
        | llm
        | {"response": lambda x: x.content}
    )
    response = chain.invoke({"schema_str": schema_str, "today_str": today_str, "user_input": user_input})
    parsed_input = json.loads(response["response"])

    if parsed_input["data"] is None:
        return False, parsed_input["message"]
    else:
        return True, parsed_input["data"]

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

def generate_plan(llm: LLM, user_input: str, parsed_input: dict, travel_info: dict) -> str:
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt2)
    user_prompt_template = HumanMessagePromptTemplate.from_template("{user_input}")
    prompt = ChatPromptTemplate.from_messages([system_prompt_template, user_prompt_template])

    chain = (
        {
            "parsed_input": lambda x: x["parsed_input"],
            "travel_info": lambda x: x["travel_info"],
            "user_input": lambda x: x["user_input"]
        }
        | prompt
        | llm
        | {"response": lambda x: x.content}
    )
    response = chain.invoke({
        "parsed_input": parsed_input,
        "travel_info": travel_info,
        "user_input": user_input
    })
    return response["response"]

def generate_travel_info_search_summary(llm: LLM, travel_info_category: str, search_info: dict, user_input: dict, preference:str="") -> str:
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt3)
    user_prompt_template = HumanMessagePromptTemplate.from_template("{user_input}")
    prompt = ChatPromptTemplate.from_messages([system_prompt_template, user_prompt_template])

    chain = (
        {
            "travel_component": lambda x: x["travel_component"],
            "info_json": lambda x: x["info_json"],
            "preference": lambda x: x["preference"],
            "user_input": lambda x: x["user_input"]
        }
        | prompt
        | llm
        | {"response": lambda x: x.content}
    )
    response = chain.invoke({
        "travel_component": travel_info_category,
        "info_json": search_info,
        "preference": preference,
        "user_input": user_input
    })
    print(response["response"])
    return response["response"]

def city_to_latlon(llm: LLM, city_name: str, additional_info: str) -> dict:
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt5)
    prompt = ChatPromptTemplate.from_messages([system_prompt_template])

    chain = (
        {
            "city_name": lambda x: x["city_name"],
            "additional_info": lambda x: x["additional_info"],
        }
        | prompt
        | llm
        | {"response": lambda x: x.content}
    )
    response = chain.invoke({
        "city_name": city_name,
        "additional_info": additional_info
    })
    return json.loads(response["response"])

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
    user_prompt_template = HumanMessagePromptTemplate.from_template("{user_input}")
    prompt = ChatPromptTemplate.from_messages([system_prompt_template, user_prompt_template])

    chain = (
        {  
            "interest_categories": lambda x: x["interest_categories"],
            "user_input": lambda x: x["user_input"]
        }
        | prompt
        | llm
        | {"response": lambda x: x.content}
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
   
    prompt = ChatPromptTemplate.from_messages([system_prompt_template])
    today_str = date.today().isoformat()
    while True:
        chain = (
            {
                "today_date": lambda x: x["today_date"],
                "validation_rule": lambda x: x["validation_rule"],
                "user_input": lambda x: x["user_input"],
            }
            | prompt
            | llm
            | {"response": lambda x: x.content}
        )
        response = chain.invoke({
            "today_date": today_str,
            "validation_rule": prompt_validation[travel_info_category],
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


def validate_user_input_single_api_call_app(llm: LLM, travel_info_category: str, user_input: dict) -> str:
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
    today_str = date.today().isoformat()
    prompt = ChatPromptTemplate.from_messages([
        system_prompt_template, 
    ])

    chain = (
        {   
            "today_date": lambda x: x["today_date"],
            "validation_rule": lambda x: x["validation_rule"],
            "user_input": lambda x: x["user_input"],
        } 
        | prompt 
        | llm
        | {"response": lambda x: x.content}
    )
    response = chain.invoke({"today_date": today_str, "validation_rule": prompt_validation[travel_info_category], "user_input": user_input})
    print(response)
    output = json.loads(response["response"])

    if output["validity"]:
        return True, "✅ All fields valid.", []
    else:
        return False, f"🚫 {output['message']}", output["invalid_fields"]


def refetch_check(llm: LLM, original_information:str, original_input: dict, additional_requirement:str, original_plan:str, user_input_schema:str)-> tuple:
    """
    The function call LLM determine if additional information is needed in order to improve the plan based on user's need.

    Args:
        original_information (str): the travel information from the original fetch
        original_input: the original user input parsed
        additional_requirement (str): user's additional requirements
        origional_plan (str): original plan needed to get refined
        user_input_schema (str): the address of the user input schema

    Return:
        (refetch (bool), fields (list), refetch_json (dict))
    """

    with open(user_input_schema, "r") as f:
        schema_str = json.load(f)

    #system prompt
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt_determine_refetch)

    prompt = ChatPromptTemplate.from_messages([
        system_prompt_template, 
    ])
    
    chain = (
        {   "information": lambda x: x["information"],
            "user_input": lambda x: x["user_input"],
            "additional_requirement": lambda x: x["additional_requirement"],
            "original_plan": lambda x: x["original_plan"],
            "user_input_json": lambda x: x["user_input_json"]
        } 
        | prompt 
        | llm
        | {"response": lambda x: x.content} 
    )
    response = chain.invoke({"information": original_information, "user_input": original_input, "additional_requirement": additional_requirement, "original_plan":original_plan, "user_input_json":schema_str})
    print("response:\n", response)
    output = response["response"]
    output = json.loads(output)
    print(output)
    if "properties" in output["refetch_json"]:
        return output["refetch"], output["fields"], output["refetch_json"]["properties"]
    else:
        return output["refetch"], output["fields"], output["refetch_json"]



def refine_plan(llm: LLM, original_plan: str, additional_requirement:str, additional_information: dict, original_info: dict):
    """
    The function call LLM to improve the plan based on user's additional requirements

    Args:
        original_info (str): the travel information from the original fetch
        additional_information (dict): additional information fetched
        additional_requirement (str): user's additional requirements
        origional_plan (str): original plan needed to get refined
        
    Return:
        a refined plan
    """


    #system prompt
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt_inprove)

    prompt = ChatPromptTemplate.from_messages([
        system_prompt_template, 
    ])
    
    chain = (
        {   "additional_requirement": lambda x: x["additional_requirement"],
            "original_plan": lambda x: x["original_plan"],
            "original_info": lambda x: x["original_info"],
            "additional_information": lambda x: x["additional_information"],
        } 
        | prompt 
        | llm
        | {"response": lambda x: x.content} 
    )
    response = chain.invoke({"additional_requirement": additional_requirement, "original_plan": original_plan, "original_info":original_info, "additional_information": additional_information})
    output = response["response"]
    return output
    
