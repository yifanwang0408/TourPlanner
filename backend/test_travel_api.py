from travel_api import (Hotel_LiteAPI, Hotel_RapidAPI, Weather_WeatherAPI, Directions_OpenRouteService, FutureFlight_Aviationstack, Attractions_API, Restaurant_API)

hotel_rapid = Hotel_RapidAPI("Hotel Rapid API")
hotel_lite = Hotel_LiteAPI("Hotel Lite API","https://api.liteapi.travel")
weather_weatherapi = Weather_WeatherAPI("Weather Forecast")
direction = Directions_OpenRouteService("Directions (OpenRouteService)")
furture_flight = FutureFlight_Aviationstack("Future Flight Schedules (Aviationstack)")
site_visit = Attractions_API("FoursquareAPI")
restaurant = Restaurant_API("Restaurant api")


def test_travel_apis():

    print("\n--- Testing Hotel Search ---")
    params_hotel = {"city": "Paris", "countryCode": "FR", "minRating": 8, "starRating": 4, "limit": 3, "aiSearch": "Hotels near Effel tower"}
    hotels = hotel_lite.get_hotel_list(url="https://api.liteapi.travel/v3.0/data/hotels",params=params_hotel)
    if hotels:
        print(hotels)
    else:
        print("No hotel data returned.")

    print("\n--- Testing Weather Forecast ---")
    params_weather = {"city": "Paris", "date": "2025-08-01"}
    weather = weather_weatherapi.get_forecast(params_weather)
    print(weather)

    print("\n--- Testing Directions ---")
    params_direction = {"start_lon": 2.3522, "start_lat": 48.8566, "end_lon": 2.295, "end_lat": 48.8738}
    # Coordinates format: [longitude, latitude]
    directions = direction.get_directions(params_direction)  # Paris city center to Eiffel Tower
    if directions:
        print(f"Route summary: {directions.get('routes', [{}])[0].get('summary', {})}")
    else:
        print("No directions data returned.")

    print("\n--- Testing Future Flight Schedules ---")
    #params_flight = {"iata_code": "JFK", "flight_type": "departure", "date": "2025-08-24"}
    params_flight = {"airport_dep": "LAX", "airport_arr": "SCL", "date_dep": "2025-09-01", "date_arr": "2025-09-01"}
    flights = furture_flight.get_future_flight_schedules(params_flight)
    print(flights)
    if flights:
        print(f"Found {len(flights)} flights departing from LAX on 2025-09-01")
        # Print first flight details
        first_flight = flights[0]
        print(f"First flight info:\n Airline: {first_flight.get('airline', {}).get('name')}\nFlight Number: {first_flight.get('flight', {}).get('iataNumber')}\nDeparture Time: {first_flight.get('departure', {}).get('scheduledTime')}")
    else:
        print("No flight schedule data returned.")


    print("\n--- Testing attraction Search ---")
    params = {
        "ll": "48.8566,2.3522",
        "radius": 10000,
        "category": "4bf58dd8d48988d1e2931735"
    }
    attractions = site_visit.get_attractions(params, limit=10)
    if(attractions):
        print(attractions)
    else:
        print("No attraction data returned.")

    print("\n--- Testing restaurant Search ---")
    params = {
        "ll": "48.8566,2.3522",
        "radius": 10000,
        "fsq_category_ids": "4d4b7105d754a06374d81259",
        "quary": "Franch food"
    }
    restaurants = restaurant.get_restaurant(params, limit=5)
    if(restaurants):
        print(restaurants)
    else:
        print("No restaurant data returned.")



if __name__ == "__main__":
    test_travel_apis()
