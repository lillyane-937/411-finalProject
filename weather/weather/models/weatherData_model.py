mport hashlib
import logging
import os

from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError

from weather.db import db
from weather.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

import logging
from typing import List, Dict
from weather_dashboard.api.weather_api import fetch_current_weather
from weather_dashboard.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

class WeatherData:
    """In-memory model to manage current weather locations."""

    def __init__(self):
        """Initialize the in-memory weather storage."""
        self.weather_records: List[Dict] = []

    def add_location(self, city_name: str) -> None:
        """Fetch weather for a city and add it to memory.

        Args:
            city_name (str): The name of the city to fetch weather for.
        """
        logger.info(f"Adding weather data for city: {city_name}")
        try:
            data = fetch_current_weather(city_name)
            if not data:
                raise ValueError(f"No weather data found for city: {city_name}")

            weather_entry = {
                "city_name": data["name"],
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "cloudiness": data["clouds"]["all"],
                "pressure": data["main"]["pressure"]
            }
            self.weather_records.append(weather_entry)
            logger.info(f"Weather data added for {city_name}")

        except Exception as e:
            logger.error(f"Failed to add weather data for {city_name}: {e}")
            raise

    def get_all_locations(self) -> List[Dict]:
        """Return all stored weather records."""
        logger.info(f"Retrieving all weather data ({len(self.weather_records)} records).")
        return self.weather_records

    def clear_locations(self) -> None:
        """Clear all weather records from memory."""
        if not self.weather_records:
            logger.warning("Attempted to clear an empty weather list.")
            return
        logger.info("Clearing all stored weather data.")
        self.weather_records.clear()
