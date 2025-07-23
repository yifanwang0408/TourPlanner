from travel_api import (get_directions, get_future_flight_schedules,
                        get_weather_forecast, search_hotels)


def main():
    while True:
        print("\n--- Tour Planner CLI ---")
        print("1. Search Hotels")
        print("2. Get Weather Forecast")
        print("3. Get Directions")
        print("4. Get Future Flight Schedules")
        print("5. Exit")

        choice = input("Choose an option (1-5): ")

        if choice == "1":
            city = input("Enter city: ")
            check_in = input("Enter check-in date (YYYY-MM-DD): ")
            check_out = input("Enter check-out date (YYYY-MM-DD): ")
            adults = int(input("Enter number of adults: "))
            result = search_hotels(city, check_in, check_out, adults)
            print("\nSearch Hotels Result:\n", result)

        elif choice == "2":
            city = input("Enter city: ")
            result = get_weather_forecast(city)
            print("\nWeather Forecast:\n", result)

        elif choice == "3":
            start_lon = float(input("Enter start longitude: "))
            start_lat = float(input("Enter start latitude: "))
            end_lon = float(input("Enter end longitude: "))
            end_lat = float(input("Enter end latitude: "))
            start_coords = [start_lon, start_lat]
            end_coords = [end_lon, end_lat]
            result = get_directions(start_coords, end_coords)
            print("\nDirections:\n", result)

        elif choice == "4":
            airport = input("Enter airport IATA code: ")
            flight_type = input("Enter flight type (arrival/departure): ")
            date = input("Enter date (YYYY-MM-DD): ")
            result = get_future_flight_schedules(airport, flight_type, date)
            print("\nFlight Schedules:\n", result)

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
