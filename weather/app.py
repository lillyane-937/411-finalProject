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
from weather.models.user_model import User
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