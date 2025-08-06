hotel_input_prompt = {
    "city": "Enter city: ", 
    "countryCode": "Enter countryCode of where the city is located in: ", 
    "hotelName": "Enter hotel name: ", 
    "minRating": "Enter the minimum rating of the hotel: ", 
    "starRating": "Enter the star rating of the hotel(star ratings have 2 allowed decimals '.0' and '.5' from 1 to 5. e.g. '3.5,4.0,5.0'): "
}

weather_input_prompt = {
    "city": "Enter city: ", 
    "date":"Enter date (YYYY-MM-DD): "
}

direction_input_prompt = {
    "start_lon": "Enter start longitude: ", 
    "start_lat": "Enter start latitude: ", 
    "end_lon": "Enter end longitude: ", 
    "end_lat": "Enter end latitude: "
}
furture_flight_input_prompt = {
    "airport_dep": "Enter departure airport IATA code:", 
    "airport_arr": "Enter arrival airport IATA code: ", 
    "date_dep": "Enter departure date (YYYY-MM-DD): ", 
    "date_arr": "Enter arrival date (YYYY-MM-DD): "
}

site_visit_prompt = {
    "city": "Enter the city that you want to visit: ", 
    "additional_info": "Additional info to help us locate the city: ", 
    "interest": "Enter your interest (e.g. attraction): ", 
}

restaurant_prompt = {
    "city": "Enter the city that you want to visit: ", 
    "additional_info": "Additional info to help us locate the city: ", "food_preference":"Enter your interest on food (e.g. restaurant): "
}


from tools import categorize_user_input, city_to_latlon, validate_user_input_single_api_call
from travel_api import FutureFlight_Aviationstack, Hotel_LiteAPI
from places_category_id import site_categories, restaurant_categories, site_categories_str, restaurant_categories_str

def reprompt_until_valid(llm, category: str, user_input: dict, prompt_dict: dict, validator_function):
    """
    Keep reprompting user until input is valid.
    """
    validity, message, invalid_fields = validator_function(llm, category, user_input)

    while not validity:
        print(f"\n[!] {message}")
        retry = input("Do you want to re-enter the missing/invalid fields? (yes/no): ").strip().lower()
        if retry not in ["yes", "y"]:
            print("User chose not to re-enter. Aborting.")
            return None

        for field in invalid_fields:
            prompt = prompt_dict.get(field, f"Enter value for {field}: ")
            new_value = input(prompt)
            user_input[field] = new_value

        validity, message, invalid_fields = validator_function(llm, category, user_input)

    return user_input


class Prompt_API_Search():
    def __init__(self):
        pass

    def prompt_hotel(self, llm) -> dict:
        """
        initial prompt for hotel
        """
        user_input = {
            "city": input(hotel_input_prompt["city"]),
            "countryCode": input(hotel_input_prompt["countryCode"]),
        }
        has_hotel_name = input("Do you have a hotel(name) that you want to look for (yes/no)?: ").strip().lower()
        if has_hotel_name in ["yes", "y"]:
            user_input["hotelName"] = input(hotel_input_prompt["hotelName"])
        user_input["minRating"] = input(hotel_input_prompt["minRating"])
        user_input["starRating"] = input(hotel_input_prompt["starRating"])

        validated_input = reprompt_until_valid(
            llm, "hotel", user_input, hotel_input_prompt, validate_user_input_single_api_call
        )

        if validated_input is None:
            return None

        has_preference = input("Do you have any preference on hotel? e.g. Hotels near Eiffel tower? (yes/no)?: ").strip().lower()
        if has_preference in ["yes", "y"]:
            validated_input["aiSearch"] = input("Enter your preference: ")

        return validated_input
    

    def prompt_weather(self, llm) -> dict:
        user_input = {
            "city": input(weather_input_prompt["city"]),
            "date": input(weather_input_prompt["date"])
        }
        return reprompt_until_valid(
            llm, "weather", user_input, weather_input_prompt, validate_user_input_single_api_call
        )

    def prompt_direction(self, llm) -> dict:
        user_input = {
            "start_lon": input(direction_input_prompt["start_lon"]),
            "start_lat": input(direction_input_prompt["start_lat"]),
            "end_lon": input(direction_input_prompt["end_lon"]),
            "end_lat": input(direction_input_prompt["end_lat"])
        }
        return reprompt_until_valid(
            llm, "direction", user_input, direction_input_prompt, validate_user_input_single_api_call
        )

    def prompt_furture_flight(self, llm) -> dict:
        user_input = {
            "airport_dep": input(furture_flight_input_prompt["airport_dep"]),
            "airport_arr": input(furture_flight_input_prompt["airport_arr"]),
            "date_dep": input(furture_flight_input_prompt["date_dep"]),
            "date_arr": input(furture_flight_input_prompt["date_arr"])
        }
        return reprompt_until_valid(
            llm, "flight", user_input, furture_flight_input_prompt, validate_user_input_single_api_call
        )
    
    def prompt_site_visit(self, llm) -> dict:
        """
        initial prompt for places to visit
        """
        params = {}
        city = input("Enter the city that you want to visit: ")
        additional_info = input("Additional info to help us locate the city: ")
        interest = input("Enter your interest (e.g. attraction): ")

        response  = city_to_latlon(llm, city, additional_info)
        params["ll"] = response["ll"]
        params["radius"] = response["radius"]

        interests = categorize_user_input(llm, interest, site_categories_str)
        params["category"] = transfer_interest_id(interests["categories"], site_categories)
        return params

    def prompt_restaurant(self, llm):
        """
        initial prompt for restaurant
        """
        params = {}
        city = input("Enter the city that you want to visit: ")
        additional_info = input("Additional info to help us locate the city: ")
        food_preference = input("Enter your interest on food (e.g. restaurant): ")

        response  = city_to_latlon(llm, city, additional_info)
        params["ll"] = response["ll"]
        params["radius"] = response["radius"]
        interests = categorize_user_input(llm, food_preference, restaurant_categories_str)
        params["fsq_category_ids"] = transfer_interest_id(interests["categories"], restaurant_categories)

        return params
        


def process_hotel_query_params(parsed_input, limit = 4, aiSearch = None):
    """
    This function is for proces hotel info from Liteapi travel

    Args:
        parsed_input: parsed user input
        limit: number of hotel fetch for each city
        aiSearch: additional requirement on hotel, such as hotel near shopping center

    Return:
        parameters for api call to fetch hotel information and a list of city
    """
    #for each city traveled to, generate query to fetch hotel
    days = parsed_input["daily_plan"]
    list_params = []
    city_list = [] 

    for day in days:
        param = {}
        param["countryCode"] = day["country_code"]
        param["cityName"] = day["city"]
        if day["accomondation"]["hotel_name"] != "":
            param["hotelName"] = day["accomondation"]["hotel_name"]
        param["starRatingparam"] = day["accomondation"]["hotel_rating"]
        param["limit"] = limit
        if aiSearch != None:
            param["aiSearch"] = aiSearch
        list_params.append(param)
        city_list.append(day["city"])
    return list_params, city_list


def process_flight_quary_params(parsed_input):
    """
    This function is for proces flight info from Aviationstack

    Args:
        parsed_input: parsed user input

    Return:
        parameters for api call to fetch flight information
    """
    list_params = []
    for flight in parsed_input["flights"]:
        param = {}
        param["airport_dep"] = flight["departure_iata"]
        param["airport_arr"] = flight["arrival_iata"]
        param["date_dep"] = flight["departure_date"]
        param["date_arr"] = flight["arrival_date"]
        list_params.append(param)
    return list_params


def get_weather_params(data):
    """
    This function is for proces weather info for each day 

    Args:
        parsed_input: parsed user input

    Return:
        parameters for api call to fetch weather information
    """
    days = data["daily_plan"]
    list_params = []
    for day in days:
        param = {}
        param["lat"] = day["city_lat"]
        param["lon"] = day["city_lon"]
        param["city"] = day["city"]
        param["date"] = day["date"]
        list_params.append(param)
    return list_params

def transfer_interest_id(interests:list, interest_dict:dict):
    """
    The function transfer string of interest into their id used to fetch data from api

    Args:
        interests (list(str)): user interests
        interest_dict: the interest dict where the key is the interest str, and the value is the interest id
    
    Return:
        string of interest id
    """
    interest_string = ""
    index = 0
    for interest in interests:
        interest_id = interest_dict[interest]
        if index == 0:
            interest_string += interest_id
        else:
            interest_string += "," + interest_id
        index += 1
    return interest_string

def transfer_restaurant_id(interest):
    return restaurant_categories[interest]

def get_site_params(data):
    """
    This function get the parameters to fetch places to visit fro api

    Args:
        data: parsed user input

    Return:
        a list of parameters for api call to fetch places to visit information, and keys to get the value of the dictionary
    """
    site_params = []
    keys_list = []
    days = data["daily_plan"]
    for day in days:
        param = {}
        param["ll"] = f"{day['city_lat']},{day['city_lon']}"
        param["radius"] = day["city_radius"]

        param["category"] = transfer_interest_id(day["places_visit"], site_categories)

        site_params.append(param)
        keys_list.append((day["city"], day["date"]))
    return site_params, keys_list



def output_travel_info(daily_plan):
    """
    Out put travel info by day
    """
    for plan in daily_plan:
        print(plan["day_title"])
        activities = plan["activities"]
        for activity in activities:
            print(activity["activity_description"])
        print(plan["extra_tip"])


def process_meal_params(data):
    """
    This function process meal parameters from parsed user input

    Args:
        data: parsed user input

    Return:
        a parameter dictionary where the key is (city, date, type of meal), and the value is the parameters for api call, and a list of keys
    """
    days = data["daily_plan"]
    index_other = 0
    param_dict = {}
    keys = []
    for day in days:
        food_list = day["food"]
        ll = f"{day['city_lat']},{day['city_lon']}"
        radius = day["city_radius"]
        for meal in food_list:
            param = {}
            param["ll"] = ll
            param["radius"] = radius
            param["fsq_category_ids"] = transfer_interest_id(meal["type_food"], restaurant_categories)
            

            if("extra_requirement" != ""):
                param["query"] = meal["extra_requirement"]

            if(meal["type_meal"] != "other"):
                param_dict[day["city"], day["date"], meal["type_meal"]] = param
                keys.append((day["city"], day["date"], meal["type_meal"]))
            else:
                param_dict[(day["city"], day["date"], "other" + str(index_other))] = param
                keys.append((day["city"], day["date"], "other" + str(index_other)))
                index_other += 1
    return param_dict, keys

        
            
     
def fetch_all_travel_info(data, hotel, flight, weather, attraction, restaurant):
    """
    Fetch all travel info

    Args:
        data: parsed user input
        hotel: the hotel api class
        flight: the flight api class
        weather: the weather api class
        attraction: the attraction api class
        restaurant: the restaurant api class

    Return:
        a dictionary including all travel information, where the key is category of info, and the value is the info fetched from api..
    """
    travel_info = {}
    
    #hotel info
    hotel_params, city_list = process_hotel_query_params(data)
    hotel_list = hotel.get_hotel("https://api.liteapi.travel/v3.0/data/hotels", hotel_params, city_list)
    travel_info["hotel"] = hotel_list

    #flight info
    flight_params = process_flight_quary_params(data)
    flight_list = flight.process_several_flights(flight_params)
    travel_info["flight"] = flight_list

    #weather info
    weather_params = get_weather_params(data)
    weather_list = weather.get_weather_multidays(weather_params)
    travel_info["weather"] = weather_list

    #attraction info
    site_params, keys_list = get_site_params(data)
    site_list = attraction.get_attraction_list(site_params, keys_list)
    travel_info["site"] = site_list

    #Restaurant info
    meal_params, meal_keys = process_meal_params(data)
    meal_list = restaurant.get_restaurant_list(meal_params, meal_keys)
    travel_info["meal"] = meal_list

    return travel_info
           

