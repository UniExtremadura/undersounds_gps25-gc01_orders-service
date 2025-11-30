import os
import requests
from dotenv import load_dotenv
from circuitbreaker import CircuitBreaker
import py_eureka_client.eureka_client as eureka_client

load_dotenv()

class Config:
    """Base config"""
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://mendo:12345@orders-service-db:3306/orders_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Keycloak
    KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://keycloak:8080")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_MICROSERVICE_CLIENT_ID", "orders-service")
    KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "undersounds")
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_MICROSERVICE_CLIENT_SECRET", "prueba-no-real")
    
    # Application
    SERVICE_NAME = "Servicio de Compras"
    SERVICE_VERSION = "1.0.0"
    
    # Swagger
    SWAGGER_URL = '/api/v1/ui'
    API_URL = '/api/v1/swagger.json'

    # INTRA communication
    USERS_SERVICE_URL = os.getenv("USERS_URL", "http://localhost:8081")
    CONTENT_SERVICE_URL = os.getenv("CONTENT_URL", "http://content-service:8080")
    PAYMENT_SERVICE_URL = os.getenv("PAYMENT_URL", "http://payment-service:8082")
    NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_URL", "http://notifications-service:8085")

    # Configuración de Eureka
    EUREKA_SERVER = os.getenv('EUREKA_SERVER', "http://localhost:8761")
    APP_NAME = os.getenv('APP_NAME', 'orders-service')
    INSTANCE_PORT = int(os.getenv('INSTANCE_PORT', 8084))
    INSTANCE_HOST = os.getenv('INSTANCE_HOST', 'orders-service')
    HOME_PAGE_URL = 'http://orders-service:8084'
    HEALTH_URL = 'http://orders-service:8084/api/v1/health'
    
class EurekaConfig:
    @staticmethod
    def init_eureka(app):
        """Inicializar el cliente Eureka"""
        try:

            eureka_url = "http://eureka-server:8761/eureka"

            print("Iniciando registro en Eureka...", flush=True)
            print(f"Configuración:", flush=True)
            print(f"   - Eureka Server: {eureka_url}", flush=True)
            print(f"   - App Name: {app.config.get('APP_NAME')}")
            print(f"   - Host: {app.config.get('INSTANCE_HOST')}")
            print(f"   - Port: {app.config.get('INSTANCE_PORT')}")

            eureka_client.init(
                eureka_server="http://host.docker.internal:8761/eureka",
                app_name=app.config.get('APP_NAME'),
                instance_port=app.config.get('INSTANCE_PORT'),
                instance_host=app.config.get('INSTANCE_HOST'),
                renewal_interval_in_secs=30,
                home_page_url=app.config.get('HOME_PAGE_URL'),
                health_check_url=app.config.get('HEALTH_URL'),
                duration_in_secs=90,
                metadata={
                    "version": "1.0.0",
                    "environment": "development"
                }
            )
            
            print("✅ Registrado en Eureka correctamente")
            
        except Exception as e:
            print(f"❌ Error registrando en Eureka: {e}")
            import traceback
            traceback.print_exc()   

class CircuitBreakerPersonalizado(CircuitBreaker):
    FAILURE_THRESHOLD = 7
    RECOVERY_TIMEOUT = 60
    EXPECTED_EXCEPTION = requests.exceptions.RequestException    

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