from travel_api import (get_directions, get_future_flight_schedules,
                        get_weather_forecast, search_hotels)


def test_travel_apis():
    print("\n--- Testing Hotel Search ---")
    hotels = search_hotels("Paris", "2025-12-10", "2025-12-15", adults=2)
    if hotels:
        print(f"Found {len(hotels.get('data', []))} hotels")
    else:
        print("No hotel data returned.")

    print("\n--- Testing Weather Forecast ---")
    weather = get_weather_forecast("Paris")
    print(weather)

    print("\n--- Testing Directions ---")
    # Coordinates format: [longitude, latitude]
    directions = get_directions([2.3522, 48.8566], [2.295, 48.8738])  # Paris city center to Eiffel Tower
    if directions:
        print(f"Route summary: {directions.get('routes', [{}])[0].get('summary', {})}")
    else:
        print("No directions data returned.")

    print("\n--- Testing Future Flight Schedules ---")
    flights = get_future_flight_schedules("JFK", "departure", "2025-08-24")
    if flights:
        print(f"Found {len(flights)} flights departing from JFK on 2025-08-24")
        # Print first flight details
        first_flight = flights[0]
        print(f"First flight info:\n Airline: {first_flight.get('airline', {}).get('name')}\nFlight Number: {first_flight.get('flight', {}).get('iataNumber')}\nDeparture Time: {first_flight.get('departure', {}).get('scheduledTime')}")
    else:
        print("No flight schedule data returned.")

if __name__ == "__main__":
    test_travel_apis()
