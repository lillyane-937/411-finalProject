import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)

from config import ProductionConfig
from weather.db import db
from weather.models.user_model import Users
from weather.models.weatherLocation_model import WeatherLocation
from weather.models.weatherData_model import WeatherData
from weather.utils.logger import configure_logger

load_dotenv()

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    configure_logger(app.logger)
    app.config.from_object(config_class)

    
    db.init_app(app) #set up the database
    with app.app_context():
        db.create_all()
    

    login_manager = LoginManager() #handles user login-functionality
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        return make_response(jsonify({
            "status": "error", "message": "Auth required"
        }), 401)
    
@app.route("/weather", methods=["GET"])
def get_all_weather():
    """Retrieve all weather data."""
    return jsonify(weather_data.get_all_locations()), 200

@app.route("/weather", methods=["POST"])
def add_weather():
    """Add weather data for a specific city."""
    city_name = request.json.get("city_name")
    if city_name:
        try:
            weather_data.add_location(city_name)
            return jsonify({"message": f"Weather data added for {city_name}"}), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    return jsonify({"error": "City name is required"}), 400   

@app.route("/weather/<city_name>", methods=["GET"])
def get_weather_by_city(city_name):
    """Get weather data for a specific city."""
    weather_records = [record for record in weather_data.weather_records if record['city_name'].lower() == city_name.lower()]
    if weather_records:
        return jsonify(weather_records[0]), 200
    return jsonify({"error": f"Weather data for {city_name} not found."}), 404

@app.route("/weather", methods=["DELETE"])
def clear_all_weather():
    """Clear all weather records."""
    weather_data.clear_locations()
    return jsonify({"message": "All weather data cleared."}), 200

@app.route("/weather/<city_name>", methods=["DELETE"])
def delete_weather_by_city(city_name):
    """Delete weather data for a specific city."""
    weather_data.weather_records = [record for record in weather_data.weather_records if record['city_name'].lower() != city_name.lower()]
    return jsonify({"message": f"Weather data for {city_name} deleted."}), 200

if __name__ == "__main__":
    app.run(debug=True)
