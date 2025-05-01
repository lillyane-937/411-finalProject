import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone

from weather.weather_api import get_current_weather
from weather.utils.logger import configure_logger
from weather.weather.weather_api import get_current_weather
#from utils.logger import configure_logger
from weather.weather.utils.logger import configure_logger


class WeatherData:
    """class to handle the in-memory weather storage."""

    def __init__(self):
        """Initializes the weatherRecord with an empty list of entries."""
        self.weather_records: List[Dict] = []
        self.logger = logging.getLogger(__name__)
        configure_logger(self.logger)

    def add_location(self, city_name: str) -> None:
        """
        Fetch weather data from the API and add it to the in-memory list.

        Args:
            city_name (str): The name of the city to fetch weather for.

        Raises:
            ValueError: If no weather data is returned for the given city.
            Exception: For any unexpected API or data processing error.
        """
        self.logger.info(f"Adding weather data for city: {city_name}")
        try:
            data = get_current_weather(city_name)
            if not data:
                raise ValueError(f"No weather data found for city: {city_name}")

            weather_entry = {
                "city_name": data["name"],
                "country_code": data.get("sys", {}).get("country", "N/A"),
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "cloudiness": data["clouds"]["all"],
                "pressure": data["main"]["pressure"],
                "timestamp": datetime.fromtimestamp(data["dt"], timezone.utc)
            }
            self.weather_records.append(weather_entry)
            self.logger.info(f"Weather data added for {city_name}")

        except Exception as e:
            self.logger.error(f"Failed to add weather data for {city_name}: {e}")
            raise


    def get_all_locations(self) -> List[Dict]:
        """
        Retrieve all stored weather records.

        Returns:
            List[Dict]: A list of all weather record dictionaries.
        """
        self.logger.info(f"Retrieving all weather data ({len(self.weather_records)} records).")
        return self.weather_records

    def get_weather_by_id(self, location_id: int) -> Optional[Dict]:
        """
        Retrieve a weather record by its index ID.

        Args:
            location_id (int): The index in the list to retrieve.

        Returns:
            Optional[Dict]: The weather record if found, otherwise None.
        """
        if location_id < 0 or location_id >= len(self.weather_records):
            self.logger.warning(f"Invalid location ID: {location_id}")
            return None
        self.logger.info(f"Looking for weather data with ID: {location_id}")
        return self.weather_records[location_id]

    def get_weather_by_city(self, city_name: str) -> Optional[Dict]:
        """
        Retrieve a weather record by city name.

        Args:
            city_name (str): The name of the city to retrieve data for.

        Returns:
            Optional[Dict]: The weather record if found, otherwise None.
        """
        self.logger.info(f"Looking for weather data for city: {city_name}")
        for record in self.weather_records:
            if record["city_name"].lower() == city_name.lower():
                return record
        self.logger.warning(f"No weather data found for city: {city_name}")
        return None

    def delete_weather_by_id(self, location_id: int) -> None:
        """
        Delete a weather record by its index ID.

        Args:
            location_id (int): The index of the record to remove.
        """
        if location_id < 0 or location_id >= len(self.weather_records):
            self.logger.warning(f"Invalid location ID: {location_id}")
            return
        deleted = self.weather_records.pop(location_id)
        self.logger.info(f"Deleted weather data for city: {deleted['city_name']}")

    def delete_weather_by_city(self, city_name: str) -> None:
        """
        Delete all records matching a given city name.

        Args:
            city_name (str): The city name whose data should be removed.
        """
        before = len(self.weather_records)
        self.weather_records = [
            record for record in self.weather_records
            if record["city_name"].lower() != city_name.lower()
        ]
        if len(self.weather_records) < before:
            self.logger.info(f"Deleted weather data for city: {city_name}")
        else:
            self.logger.warning(f"No weather data found for city: {city_name} to delete.")

    def update_weather_data(self, city_name: str) -> None:
        """
        Update the weather data for a specific city using the API.

        Args:
            city_name (str): The city to update weather data for.

        Raises:
            ValueError: If no matching record is found or API returns no data.
        """
        self.logger.info(f"Updating weather data for city: {city_name}")
        for record in self.weather_records:
            if record["city_name"].lower() == city_name.lower():
                new_data = get_current_weather(city_name)
                if not new_data:
                    raise ValueError(f"No updated data found for city: {city_name}")
                record.update({
                    "temperature": new_data["main"]["temp"],
                    "humidity": new_data["main"]["humidity"],
                    "description": new_data["weather"][0]["description"],
                    "wind_speed": new_data["wind"]["speed"],
                    "cloudiness": new_data["clouds"]["all"],
                    "pressure": new_data["main"]["pressure"],
                    "timestamp": datetime.fromtimestamp(new_data["dt"], timezone.utc)
                })
                self.logger.info(f"Weather data updated for city: {city_name}")
                return
        raise ValueError(f"Weather data for city '{city_name}' not found.")

    def clear_locations(self) -> None:
        """
        Clear all weather records from memory.

        Logs a warning if the list is already empty.
        """
        if not self.weather_records:
            self.logger.warning("Attempted to clear an empty weather list.")
            return
        self.logger.info("Clearing all stored weather data.")
        self.weather_records.clear()
        self.logger.info("All weather data cleared.")