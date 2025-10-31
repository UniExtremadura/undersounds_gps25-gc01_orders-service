import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base config"""
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Keycloak
    KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8081/")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "orders-service")
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "undersounds")
    
    # Application
    SERVICE_NAME = "Servicio de Compras"
    SERVICE_VERSION = "1.0.0"
    
    # Swagger
    SWAGGER_URL = '/api/v1/ui'
    API_URL = '/api/v1/swagger.json'

class DevelopmentConfig(Config):
    """Developement Config"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production Config"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing Config"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

# Config mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}