import logging
from typing import List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from weather.db import db
from weather.utils.logger import configure_logger

class WeatherLocation(db.Model):
    """Represents a weather entry in the database.

    This model maps to the 'locations' table in the database and stores info about the weather data
    such as city name, counter, temp, etc.
    Used in a Flask-SQLAlchemy application to
    manage weather data

    """

    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city_name = db.Column(db.String(120), nullable=False)
    country_code = db.Column(db.String(10))
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    weather_description = db.Column(db.String(120))
    wind_speed = db.Column(db.Float)
    cloudiness = db.Column(db.Integer)
    pressure = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, nullable=False)




     @classmethod
    def create_location(cls, user_id: int, weather_data: dict) -> None:
        """Create and persist a new weather location entry."""
    

        logger.info(f"Saving weather lookup for user {user_id} and city {weather_data['name']}")
         __tablename__ = 'weather_location'

        
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
        city_name = db.Column(db.String(120), nullable=False)
        country_code = db.Column(db.String(10))
        temperature = db.Column(db.Float, nullable=False)
        humidity = db.Column(db.Integer, nullable=False)
        weather_description = db.Column(db.String(120))
        wind_speed = db.Column(db.Float)
        cloudiness = db.Column(db.Integer)
        pressure = db.Column(db.Integer)
        timestamp = db.Column(db.DateTime, nullable=False)

        def __init__(
        self, user_id: int, city_name: str, country_code: str, temperature: float,
        humidity: int, weather_description: str, wind_speed: float,
        cloudiness: int, pressure: int, timestamp
    ):
        self.user_id = user_id
        self.city_name = city_name
        self.country_code = country_code
        self.temperature = temperature
        self.humidity = humidity
        self.weather_description = weather_description
        self.wind_speed = wind_speed
        self.cloudiness = cloudiness
        self.pressure = pressure
        self.timestamp = timestamp

    @classmethod
    def create_weather_location(
        cls, user_id: int, city_name: str, country_code: str, temperature: float,
        humidity: int, weather_description: str, wind_speed: float,
        cloudiness: int, pressure: int, timestamp
    ) -> None:
        """
            create a new WeatherLocation instance.

        Args:
            user_id (int):        The ID of the user performing the lookup.
            city_name (str):      The name of the city (e.g. "Boston").
            country_code (str):   The ISO country code for the city (e.g. "US").
            temperature (float):  Current temperature in Celsius.
            humidity (int):       Current humidity as a percentage (0–100).
            weather_description (str):  Short text description (e.g. "clear sky").
            wind_speed (float):   Wind speed in meters per second.
            cloudiness (int):     Cloud cover percentage (0–100).
            pressure (int):       Atmospheric pressure in hPa.
            timestamp (datetime): When the weather data was recorded (UTC).
        
        Raises:
            ValueError:           If any parameter is out of its valid range
                                  or required parameters are missing.
            IntegrityError:       If a record for this user & city already exists.
            SQLAlchemyError:      For any other database failure.
        """

        logger.info(f"Creating weather location: {city_name}, temp={temperature}°C, humidity={humidity}%")

        if not city_name:
            raise ValueError("City name must be provided.")
        if not country_code:
            raise ValueError("Country code must be provided.")
        if temperature < -100 or temperature > 100:
            raise ValueError("Temperature must be between -100°C and 100°C.")
        if humidity < 0 or humidity > 100:
            raise ValueError("Humidity must be between 0% and 100%.")
        if wind_speed < 0:
            raise ValueError("Wind speed cannot be negative.")
        if cloudiness < 0 or cloudiness > 100:
            raise ValueError("Cloudiness must be between 0% and 100%.")

        try:
            location = cls(
                user_id=user_id,
                city_name=city_name,
                country_code=country_code,
                temperature=temperature,
                humidity=humidity,
                weather_description=weather_description,
                wind_speed=wind_speed,
                cloudiness=cloudiness,
                pressure=pressure,
                timestamp=timestamp
            )
            db.session.add(location)
            db.session.commit()
            logger.info(f"Weather location created successfully for city: {city_name}")

        except IntegrityError:
            db.session.rollback()
            logger.error(f"Duplicate entry detected for city '{city_name}' for user {user_id}.")
            raise ValueError(f"Weather location '{city_name}' already exists for this user.")

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error during creation: {str(e)}")
            raise

    @classmethod
    def get_weatherlocation_by_id(cls, location_id: int) -> "WeatherLocation":
        """Retrieve a weather location by its ID.

         Args:
            location_id: The ID of the location.

        Returns:
            location: The weatherLocation instance.

        Raises:
            ValueError: If the location with the given ID does not exist.
        
        """
        location = cls.query.get(location_id)
        if location is None:
            logger.info(f"Weather location with ID {location_id} not found.")
            raise ValueError(f"Weather location with ID {location_id} not found.")
        return location

    @classmethod
    def get_weatherlocation_by_city(cls, city_name: str) -> "WeatherLocation":
        """Retrieve a weatherLocation based on its citynamr.

        Args:
            city_name: The name of the weatherLocation city.

        Returns:
            Location: The weatherLocation instance.

        Raises:
            ValueError: If the location with the given name does not exist.

        """
        location = cls.query.filter_by(city_name=city_name).first()
        if location is None:
            logger.info(f"Weather location for city '{city_name}' not found.")
            raise ValueError(f"Weather location for city '{city_name}' not found.")
        return location

    @classmethod
    def delete_weatherlocation(cls, location_id: int) -> None:
        """Delete a weatherLocation by ID.

        Args:
            location_id: The ID of the location to delete.

        Raises:
            ValueError: If the location with the given ID does not exist.

        """
        location = cls.get_weatherlocation_by_id(location_id)
        if location is None:
            logger.info(f"Weather location with ID {location_id} not found.")
            raise ValueError(f"Weather location with ID {location_id} not found.")

        db.session.delete(location)
        db.session.commit()
        logger.info(f"Weather location with ID {location_id} permanently deleted.")

    def update_weather_data(self, new_weather_data: dict) -> None:
        """Update the weatherlocation data based on any new api calls made for that city

        Args:
            self: the weatherlocation to be updated
            new_weather_data: the new entry for the newfround info for the location

        """

        logger.info(f"Updating weather data for city: {self.city_name}")

        self.temperature = new_weather_data["main"]["temp"]
        self.humidity = new_weather_data["main"]["humidity"]
        self.weather_description = new_weather_data["weather"][0]["description"]
        self.wind_speed = new_weather_data["wind"]["speed"]
        self.cloudiness = new_weather_data["clouds"]["all"]
        self.pressure = new_weather_data["main"]["pressure"]
        from datetime import datetime
        self.timestamp = datetime.utcfromtimestamp(new_weather_data["dt"])

        db.session.commit()
        logger.info(f"Weather data updated successfully for {self.city_name}.")
        
