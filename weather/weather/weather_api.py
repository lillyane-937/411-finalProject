import os
import requests
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load the API key from .env file
load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')


# Base URL for OpenWeatherMap API
BASE_URL = "https://api.openweathermap.org/data/2.5"

def get_current_weather(location):
    """
    Fetch current weather data for a given city.

    Args: location

    Returns: Parsed weather data or error message
    """
    if not API_KEY:
        error_message = "API Key is missing!"
        logging.error(error_message)
        return {"error": error_message}

    endpoint = f"{BASE_URL}/weather"
    params = {
        'q': location,
        'appid': API_KEY,
        'units': 'imperial'
    }

    try:
        logging.info(f"Requesting weather for {location}")
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        logging.info(f"Weather data fetched successfully for {location}") 
        return response.json()  
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather for {location}: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    city = input("Enter a city: ")
    weather = get_current_weather(city)

    if "error" in weather:
        print(weather["error"])
    else:
        temp = weather["main"]["temp"]
        description = weather["weather"][0]["description"]
        humidity = weather["main"]["humidity"]
        print(f"\nWeather in {city}:")
        print(f"Temperature: {temp}°F")
        print(f"Description: {description}")
        print(f"Humidity: {humidity}%")