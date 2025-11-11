import requests
from typing import Optional
from circuitbreaker import circuit
from config import CircuitBreakerPersonalizado, eureka_client
from clients.base_client import BaseClient
import logging

logger = logging.getLogger(__name__)

class UserClient(BaseClient):
    def __init__(self, app):
        super().__init__(app, "users-service")
        #self.service_name = "user-service"  # Nombre que tiene registrado Eureka para el microservicio de usuarios
        self.base_url = app.config.get('USERS_SERVICE_URL')
        self.timeout = 5
    
    def _get_user_service_url(self) -> str:
        try:
            return eureka_client.get_app_url(self.service_name)
        except Exception as e:
            logger.error(f"Error obteniendo la URL para {self.service_name}: {e}")
            return ""


    @circuit(cls=CircuitBreakerPersonalizado)
    def get_seller_by_username(self, username: str) -> Optional[dict]:
        
        try:
            
            url = f"{self.base_url}/api/artist/public/{username}"
            response = self._make_request('GET', url)
            #baseUrl = self._get_user_service_url() -> Eureka

            if response.status_code == 404:
                logger.error("No retorna nada")
                return None

            response.raise_for_status()

            return response.json()

        except requests.exceptions.ConnectionError as e:
            logger.error("Servidor de usuarios no disponible")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al intentar obtener el usuario {username}: {e}")    
            return None    