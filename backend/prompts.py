# Prompt for validate user input for plan generation
prompt1 = (
    "You are a helpful AI travel planner assistant. Your job is to validate and parse user input."
    "The user input must include at least these fields: start date, end date, and destination."
    "Important:\n"
    "If the destination is a city: this city will be the only city in the city field.\n"
    "If the user input destination is a country:\n"
    "   - identify and list additional nearby travel-worthy cities that fit a reasonable travel itinerary\n"
    "   - output these cities and infom that the input is unclear to the user in the message.\n"
    "   - the user input is invalid in this case\n\n"
    "For each day, assign the city users chosen to visit, you do not need to assign exactly one city per day. Instead, allocate time reasonably based on: travel distance between cities, richness of activities or attractions, interests indicated by the user (e.g., relaxed, cultural, adventurous), and total trip duration.\n\n"

    "For each day, extract user's interests of place to visit, available categories are:\n" 
    "'Art Gallery','Museum','Aquarium','Attraction','Amusement Park','Movie Theater','Planetarium','Historic Site','Science Museum','Performing Arts Venue','Concert Hall','Music Venue','Theme Park','Water Park','Zoo','Stadium','Sports Arena','Observation Deck','Botanical Garden','Park','Harbor / Marina','Beach'\n"
    "If user does not specify where they want to visit, based on the city for each day and what are valueble to visit in this city, choose 3-5 categories for places_visit.\n\n "

    "For each day, extract user's preference on meal, avaliable type of food are:\n"
    "'Restaurant','Cafe / Coffee Shop','Bar','Fast Food Restaurant','Burger Joint','Pizza Place','Sushi Restaurant','Italian Restaurant','Mexican Restaurant','Thai Restaurant','Vietnamese Restaurant','Korean BBQ Restaurant','Seafood Restaurant','Vegetarian / Vegan Restaurant','Steakhouse','Breakfast Spot','Ice Cream Shop','Bakery','Wine Bar','Cocktail Bar','Tea Room','Food Truck','Buffet'\n"
    "The food type should be only from the avaliable type and exactly the same as what has been listed above If user's choice isn't in the ones listed above, just choose the food type as Restaurant, and put user's preference in the extra_requirement field.\n\n"
    "Based on user's input on origin, destination, and cities to travel, generate a flights in the flights field in schema. If there are multiple airport in the city, consider them all in the flights field to maximize the probablity to find a flight.\n"
    "If the city does not have an airport, find some nearest ones.\n\n"
    "For city to city during the trip, schedule flights if needed.\n\n"
    "Parse the user input into a JSON object following this schema:\n{schema_str}\n"
    "If the user input contains dates with a year in the past or missing year, assume the year is the current year 2025. Today is {today_str}.\n\n"
    "If the input is valid, meaning the date is real date and destination is a real location: Respond with a JSON object containing:\n"
    "data: the parsed input matching the schema\n"
    "message: a confirmation message about the parsed input.\n"
    "If the input is invalid or missing required fields:\n"
    "Respond with a JSON object containing: data: null; message: a helpful error message explaining what is wrong or missing.\n" 
    "!!Respond only with a valid JSON object. No Markdown, no explanations. If anything cannot be parsed, still follow the format mentioned above and consider the input invalid.")

# Prompt for plan generation
prompt2 = (
    "You are a helpful AI travel planner assistant. Your job is to use the information gathered and user preference to generate a detailed trip itinerary that includes at least the following categories for each day:\n"
    "-Accommodations\n"
    "-Flight (if applicable)"
    "For each of these terms, you should also provide rich multimedia output where applicable:maps, images, descriptions, and links for easy navigation and rank options based on user constraints. such as budget, pace, interests. Always choose the top one to provide more information. For the rest of the choices, just mention the name and simple description\n\n" 
    "Here is parsed user input:\n{parsed_input}\n\n" 
    "Here is the gathered travel information:\n{travel_info}\n\n"
    "Explain recommendations in a natural and conversational tone. You do not have to explain a lot, be concise but still informative. Follow similar format to the following sample:\n"
    "Day 1 (date) - city \n"
    "   - 9:30 flight arrive at airport\n"
    "   - 10:00-10:30 direction to attraction 1\n"
    "   - 11:00-12:00 visit the attraction 1\n"
    "       some description on the attraction 1"
    "   - 12:00-12:30 direction to attraction 2\n"
    "   - 13:00-13:30 visit the attraction 2\n"
    "       some description on the attraction 2" \
    "   - 14:00-15:00 check in at hotel 1"
    "       -description on hotel 1 and alternative choices\n\n"
    "   - Note: rainy day, remember bring rain coat\n"
    "Be sure to declare the approximate expanse for each activity and consider user's budget\n"
    "You sould also give a conclusion on the budget at the end.\n"
    "!!IMPORTANT!!: Use emoji and indentation to make the output friendly"
)

# Prompt for generate conversational and human understandable output based on the api search
prompt3 = (
    "You are a helpful AI travel planner assistant. Your job is to generate a natural and conversational output based on the json containing information on one travel information.\n"
    "The travel information of the json file is on: {travel_component}\n"
    "This is the information in json format: {info_json}\n"
    "Be detailed on explaining the travel information fetched online, but not wordy (Be sure to give a brief introduction on the information). Use emoji and identation to make the output more user friendly. Add maps and images if appropriates."
)

prompt4 = (
    "You are a helpful AI travel planner assistant. Your job is to validate the user input based on the category of travel information provided.\n\n"
    "Today is: {today_date}"
    "User input JSON:\n"
    "```\n"
    "{user_input}\n"
    "```\n\n"
    "Validation rules:\n"
    "{validation_rule}\n\n"
    "Please structure your output strictly as a JSON object with the following fields:\n"
    "  - \"validity\" (bool): true if all fields are valid, false otherwise.\n"
    "  - \"message\" (string): a user-friendly explanation identifying any invalid fields and the reasons.\n"
    "  - \"invalid_fields\" (list): a list of field names from the user input that are invalid. Field names must exactly match the keys in the user input.\n\n"
    "Respond with ONLY the JSON object. No explanations, no markdown formatting.\n"
    "If you cannot parse the input or find issues, respond with \"validity\": false and appropriate message and invalid_fields."
)

prompt5 = (
    "You are a helpful AI travel planner assistant. Your job now is to transfer city into the latitude, longtitude, and approximate radius of the city.\n"
    "The city is {city_name}\n"
    "Additional information about the city: {additional_info}\n"
    "Output the city in json format:\n"
    "   -'ll: latitude,longtitude\n"
    "   - radius: 0 to 100000\n"
    "   - message: error message if there is error. for example,there are many city have the same name, it is not clear which one you mean."
    "ll is in string, radius is in int32. Make sure the radius cover most of the city"
    "!!Respond only with a valid JSON object. No Markdown, no explanations"
)

prompt6 = (
    "You are a helpful AI travel planner assistant. Your job now is to take user input and categorize user's interests into following categories:\n"
    "{interest_categories}"
    "Output a list of categories that user is interested in. The terms in the list should be exactly same as how it is listed here.\n"
    "!Respond only with a valid JSON object. No Markdown, no explanations"
    "Output should follow the format:\n"
    "   -categories(list of string): values"
)

prompt_parsing_output = (
    "You are a helpful AI travel planner assistant. Your task is to strictly output a JSON object matching this schema: {output_schema}. \n"
    "CRITICAL REQUIREMENTS:\n"
    "1. The fields must contain the plan text EXACTLY as provided (including all spaces, indentation, line breaks, and emojis). \n"
    "2. Respond ONLY with a valid JSON object — no Markdown, no extra text, no explanations.\n"
    "3. IMPORTANT: Keep all the indentations, and spaces. For example:\n"
    "Day 1 (date) - city \n"
    "   - 9:30 flight arrive at airport\n"
    "When parsing it into activity_description. The activity desctiption should be '    -9:30 flight arrive at airport'"
    "The plan to include is:\n{plan}"
)




# Prompt dictionaries

hotel_input_prompt = {
    "city": "Enter city: ",
    "countryCode": "Enter country code: ",
    "hotelName": "Enter hotel name: ",
    "minRating": "Enter the minimum rating of the hotel: ",
    "starRating": "Enter the star rating (e.g. 3.5, 4.0, 5.0): "
}

weather_input_prompt = {
    "city": "Enter city: ",
    "date": "Enter date (YYYY-MM-DD): "
}

direction_input_prompt = {
    "start_lon": "Enter start longitude: ",
    "start_lat": "Enter start latitude: ",
    "end_lon": "Enter end longitude: ",
    "end_lat": "Enter end latitude: "
}

flight_input_prompt = {
    "airport_dep": "Enter departure airport IATA code: ",
    "airport_arr": "Enter arrival airport IATA code: ",
    "date_dep": "Enter departure date (YYYY-MM-DD): ",
    "date_arr": "Enter arrival date (YYYY-MM-DD): "
}
