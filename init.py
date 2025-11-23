from flask import Flask, g
from config import Config, EurekaConfig
from routes import register_blueprints, register_swagger
from db import db
from auth.keycloak_config import init_keycloak
from clients import init_client
from flask_cors import CORS
import os

def create_app(config_class=Config):
    """Factory function to create Flask App"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Avoid CORS problems
    CORS(app, resources={r"/*": {"origins": "*"}}) # Permite CORS para todas las rutas y orígenes
    
    # Initialize clients
    init_client(app)

    # Initialize extensions
    initialize_extensions(app)
    
    # Registry paths and blueprints
    register_blueprints(app)
    
    # Configure Swagger UI
    register_swagger(app)
    
    # Registry handler errors
    register_error_handlers(app)

    #Subscription into Eureka's server
    #EurekaConfig.init_eureka(app)
    
    return app



def initialize_extensions(app):
    """Initialize Flask Extensions"""
    # Base de datos
    db.init_app(app)
    
    # Keycloak
    init_keycloak(app)
    
    # Otras extensiones pueden ir aquí

def register_error_handlers(app):
    """Registry global errors handler"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {
            "error": "Recurso no encontrado",
            "message": str(error),
            "status_code": 404
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            "error": "Error interno del servidor",
            "message": "Ha ocurrido un error inesperado",
            "status_code": 500
        }, 500