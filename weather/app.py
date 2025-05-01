import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from weather.config import ProductionConfig
from weather.db import db
from weather.weather.models.user_model import Users
from weather.weather.models.weatherData_model import WeatherData
from weather.weather.utils.logger import configure_logger
from flask import Flask, Response, jsonify, make_response
from flask_login import LoginManager
from flask_login import login_required
from dotenv import load_dotenv

load_dotenv()

def create_app(config_class=ProductionConfig):
    """
    Create and configure the Flask application.

    Args:
        config_class: The configuration class to use.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    #app.register_blueprint(weather_api_bp, url_prefix='/weather')
    #app.register_blueprint(auth_bp, url_prefix='/auth')

    import logging
    logger = logging.getLogger(__name__)
    configure_logger(logger)
    app.logger = logger

    
    def load_user(user_id):
        """
        Load a user from the database by their user ID.

        Args:
            user_id (str): The user's unique identifier.

        Returns:
            Users: The user instance if found, otherwise None.
        """
        app.logger.info(f"Loading user with ID: {user_id}")
        if not user_id:
            app.logger.warning("User ID is None or empty")
            return None
        return Users.query.filter_by(username=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        """
        Handle unauthorized access to protected routes.

        Returns:
            Response: A JSON response with a 401 status code.
        """
        app.logger.warning("Unauthorized access attempt")
        return make_response(jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401)

    weather_model = WeatherData()

    ####################################################
    #
    # Healthchecks
    #
    ####################################################

    @app.route('/api/health', methods=['GET'])
    def healthcheck():
        """
        Health check route to verify the service is running.

        Returns:
            Response: A JSON response indicating the service status.
        """
        app.logger.info("Health check endpoint hit")
        return make_response(jsonify({
            'status': 'success',
            'message': 'Service is running'
        }), 200)

    ##########################################################
    #
    # User Management
    #
    #########################################################

    @app.route('/api/create-user', methods=['PUT'])
    def create_user() -> Response:
        """
        Register a new user account.

        Returns:
            Response: JSON message indicating success or failure.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            Users.create_user(username, password)
            return make_response(jsonify({
                "status": "success",
                "message": f"User '{username}' created successfully"
            }), 201)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"User creation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred",
                "details": str(e)
            }), 500)

    @app.route('/api/login', methods=['POST'])
    def login() -> Response:
        """
        Authenticate and log in a user.

        Returns:
            Response: JSON message indicating login success or failure.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            if Users.check_password(username, password):
                user = Users.query.filter_by(username=username).first()
                login_user(user)
                return make_response(jsonify({
                    "status": "success",
                    "message": f"User '{username}' logged in"
                }), 200)
            else:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid credentials"
                }), 401)

        except Exception as e:
            app.logger.error(f"Login failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal login error",
                "details": str(e)
            }), 500)

    @app.route('/api/logout', methods=['POST'])
    @login_required
    def logout() -> Response:
        """
        Log out the currently authenticated user.

        Returns:
            Response: JSON message confirming logout.
        """
        logout_user()
        return make_response(jsonify({
            "status": "success",
            "message": "User logged out"
        }), 200)

    @app.route('/api/change-password', methods=['POST'])
    @login_required
    def change_password() -> Response:
        """
        Change the current user's password.

        Returns:
            Response: JSON message indicating success or failure.
        """
        try:
            data = request.get_json()
            new_password = data.get("new_password")

            if not new_password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "New password is required"
                }), 400)

            username = current_user.username
            Users.update_password(username, new_password)
            return make_response(jsonify({
                "status": "success",
                "message": "Password changed"
            }), 200)

        except Exception as e:
            app.logger.error(f"Password change failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Could not update password",
                "details": str(e)
            }), 500)

    @app.route('/api/reset-users', methods=['DELETE'])
    def reset_users() -> Response:
        """
        Recreate the users table to remove all users.

        Returns:
            Response: JSON message confirming table recreation.
        """
        try:
            app.logger.info("Received request to recreate Users table")
            with app.app_context():
                Users.__table__.drop(db.engine)
                Users.__table__.create(db.engine)
            app.logger.info("Users table recreated successfully")
            return make_response(jsonify({
                "status": "success",
                "message": f"Users table recreated successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"Users table recreation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting users",
                "details": str(e)
            }), 500)

    ##########################################################
    #
    # Weather Data Management
    #
    ##########################################################

    @app.route('/api/weather', methods=['GET'])
    def get_all_weather():
        """
        Retrieve all stored weather records.

        Returns:
            Response: JSON list of all weather entries.
        """
        app.logger.info("Fetching all weather data")
        return make_response(jsonify(weather_model.get_all_locations()), 200)

    @app.route('/api/weather', methods=['POST'])
    @login_required
    def add_weather():
        """
        Add a new weather record for a specified city.

        Returns:
            Response: JSON confirmation of addition or error.
        """
        app.logger.info("Adding new weather data")
        data = request.get_json()
        city_name = data.get("city_name")
        if not city_name:
            return make_response(jsonify({"status": "error", "message": "City name is required"}), 400)
        try:
            weather_model.add_location(city_name)
            return make_response(jsonify({"status": "success", "message": f"Weather data added for {city_name}"}), 201)
        except ValueError as e:
            return make_response(jsonify({"status": "error", "message": str(e)}), 404)

    @app.route('/api/weather/<string:city_name>', methods=['GET'])
    @login_required
    def get_weather_by_city(city_name):
        """
        Retrieve weather data for a specific city.

        Args:
            city_name (str): Name of the city to retrieve weather data for.

        Returns:
            Response: JSON data or error message.
        """
        app.logger.info(f"Fetching weather data for city: {city_name}")
        if not city_name:
            return make_response(jsonify({"status": "error", "message": "City name is required"}), 400)
        record = weather_model.get_weather_by_city(city_name)
        if record:
            return make_response(jsonify({"status": "success", "data": record}), 200)
        return make_response(jsonify({"status": "error", "message": f"Weather data for {city_name} not found"}), 404)

    @app.route('/api/weather/<string:city_name>', methods=['PUT'])
    @login_required
    def update_weather_for_city(city_name):
        """
        Update weather information for a specified city.

        Args:
            city_name (str): Name of the city to update.

        Returns:
            Response: Success or error message.
        """
        app.logger.info(f"Updating weather data for city: {city_name}")
        try:
            weather_model.update_weather_data(city_name)
            return make_response(jsonify({"status": "success", "message": f"Weather data updated for {city_name}"}), 200)
        except ValueError as e:
            return make_response(jsonify({"status": "error", "message": str(e)}), 404)

    @app.route('/api/weather/<string:city_name>', methods=['DELETE'])
    @login_required
    def delete_weather_by_city(city_name):
        """
        Delete weather data for a specified city.

        Args:
            city_name (str): Name of the city to delete.

        Returns:
            Response: JSON confirmation of deletion.
        """
        app.logger.info(f"Deleting weather data for city: {city_name}")
        weather_model.delete_weather_by_city(city_name)
        return make_response(jsonify({"status": "success", "message": f"Weather data for {city_name} deleted"}), 200)

    @app.route('/api/weather', methods=['DELETE'])
    @login_required
    def clear_all_weather():
        """
        Remove all stored weather records.

        Returns:
            Response: JSON message confirming clearing of data.
        """
        app.logger.info("Clearing all weather data")
        weather_model.clear_locations()
        return make_response(jsonify({"status": "success", "message": "All weather data cleared"}), 200)

    return app

if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Flask app...")
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")