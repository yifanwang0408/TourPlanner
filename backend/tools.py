import json
from datetime import date

from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)
from langchain.tools import tool
from llm import LLM
from prompt import prompt1, prompt2, prompt3, prompt4, prompt5, prompt6


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

def generate_travel_info_search_summary(llm: LLM, travel_info_category: str, search_info: dict, user_input: dict) -> str:
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt3)
    user_prompt_template = HumanMessagePromptTemplate.from_template("{user_input}")
    prompt = ChatPromptTemplate.from_messages([system_prompt_template, user_prompt_template])

    chain = (
        {
            "travel_component": lambda x: x["travel_component"],
            "info_json": lambda x: x["info_json"],
            "user_input": lambda x: x["user_input"]
        }
        | prompt
        | llm
        | {"response": lambda x: x.content}
    )
    response = chain.invoke({
        "travel_component": travel_info_category,
        "info_json": search_info,
        "user_input": user_input
    })
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

def categorize_user_input(llm: LLM, user_input: str) -> list:
    system_prompt_template = SystemMessagePromptTemplate.from_template(prompt6)
    user_prompt_template = HumanMessagePromptTemplate.from_template("{user_input}")
    prompt = ChatPromptTemplate.from_messages([system_prompt_template, user_prompt_template])

    chain = (
        {
            "user_input": lambda x: x["user_input"]
        }
        | prompt
        | llm
        | {"response": lambda x: x.content}
    )
    response = chain.invoke({
        "user_input": user_input
    })
    return json.loads(response["response"])
