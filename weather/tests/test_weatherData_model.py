import pytest
from datetime import datetime
from weather.models.weatherData_model import WeatherData



@pytest.fixture
def weather_model():
    """Fixture to provide a new instance of WeatherData for each test"""
    return WeatherData()


@pytest.fixture
def sample_weather_response():
    """a sample API response for mocking"""
    return {
        "name": "Boston",
        "dt": 1680000000,
        "main": {
            "temp": 30.0,
            "humidity": 68,
            "pressure": 1000
        },
        "weather": [{"description": "light rain"}],
        "wind": {"speed": 5.2},
        "clouds": {"all": 60},
        "sys": {"country": "US"}
    }


def test_clear_locations(weather_model, sample_weather_response, mocker):
    """Test that clear all weather locations in the the weather_records list
    """
    mocker.patch("weather.models.weatherData_model.fetch_current_weather", return_value=sample_weather_response)
    weather_model.add_location("Boston")
    assert len(weather_model.weather_records) == 1
    weather_model.clear_locations()
    assert len(weather_model.weather_records) == 0

def test_add_location(weather_model, sample_weather_response, mocker):
    """Test adding a new location to the weather records
    """
    mocker.patch("weather.models.weatherData_model.fetch_current_weather", return_value=sample_weather_response)
    weather_model.add_location("Boston")
    assert len(weather_model.weather_records) == 1
    assert weather_model.weather_records[0]["city_name"] == "Boston"

def test_get_weather_by_city_invalid(weather_model):
    """Test retrieving weather data by city name thats not in the records
    """
    result = weather_model.get_weather_by_city("Brooklyn")
    assert result is None, "Expected no weather data for Brooklyn"


def test_get_weather_by_id_valid(weather_model, sample_weather_response, mocker):
    """Test to get weather data by id
    """
    mocker.patch("weather.models.weatherData_model.fetch_current_weather", return_value=sample_weather_response)
    weather_model.add_location("Boston")
    result = weather_model.get_weather_by_id(0)
    assert result["city_name"] == "Boston"


def test_get_weather_by_id_invalid(weather_model, caplog):
    """Test to get weather data by invalid id
    """
    with caplog.at_level("WARNING"):
        result = weather_model.get_weather_by_id(1)
    assert result is None
    assert "Invalid location ID" in caplog.text


def test_update_weather_data(weather_model, sample_weather_response, mocker):
    """Test updating weather data
    """
    mocker.patch("weather.models.weatherData_model.fetch_current_weather", return_value=sample_weather_response)
    weather_model.add_location("Boston")

    updated_data = sample_weather_response.copy()
    updated_data["main"]["temp"] = 25
    updated_data["weather"][0]["description"] = "sunny"
    mocker.patch("weather.models.weatherData_model.fetch_current_weather", return_value=updated_data)

    weather_model.update_weather_data("Boston")
    record = weather_model.get_weather_by_city("Boston")

    assert record["temperature"] == 25
    assert record["description"] == "sunny"
