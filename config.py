import os
import requests
from dotenv import load_dotenv
from circuitbreaker import CircuitBreaker
import py_eureka_client.eureka_client as eureka_client

load_dotenv()

class Config:
    """Base config"""
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Keycloak
    KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_MICROSERVICE_CLIENT_ID")
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_MICROSERVICE_CLIENT_SECRET")
    
    # Application
    SERVICE_NAME = "Servicio de Compras"
    SERVICE_VERSION = "1.0.0"
    
    # Swagger
    SWAGGER_URL = '/api/v1/ui'
    API_URL = '/api/v1/swagger.json'

    # INTRA communication
    USERS_SERVICE_URL = os.getenv("USERS_URL")
    CONTENT_SERVICE_URL = os.getenv("CONTENT_URL")
    PAYMENT_SERVICE_URL = os.getenv("PAYMENT_URL")
    NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_URL")

    # Configuración de Eureka
    EUREKA_SERVER = os.getenv('EUREKA_SERVER')
    APP_NAME = os.getenv('APP_NAME')
    INSTANCE_PORT = int(os.getenv('INSTANCE_PORT'))
    INSTANCE_HOST = os.getenv('INSTANCE_HOST')
    HOME_PAGE_URL = 'http://localhost:5000'
    HEALTH_URL = 'http://localhost:5000/api/v1/health'
    
class EurekaConfig:
    @staticmethod
    def init_eureka(app):
        """Inicializar el cliente Eureka"""
        try:
            eureka_client.init(
                eureka_server = app.config.get('EUREKA_SERVER'), 
                app_name = app.config.get('APP_NAME'),                  
                instance_port = app.config.get('INSTANCE_PORT'),                          
                instance_host = app.config.get('INSTANCE_HOST'),                    
                renewal_interval_in_secs=30,
                home_page_url = app.config.get('HOME_PAGE_URL'),
                health_check_url = app.config.get('HEALTH_URL'),                   
                duration_in_secs=90,                          
                metadata={
                    "version": "1.0.0",
                    "environment": "development"
                }
            )
            print("✅ Registrado en Eureka correctamente")
        except Exception as e:
            print(f"❌ Error registrando en Eureka: {e}")

    @staticmethod
    def get_service_url(service_name: str) -> str:
        """Obtener URL de un servicio desde Eureka"""
        try:
            return eureka_client.get_app_url(service_name)
        except Exception as e:
            print(f"❌ Error obteniendo URL para {service_name}: {e}")
            return None        
 

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