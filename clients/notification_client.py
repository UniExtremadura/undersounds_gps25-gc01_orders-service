import requests
from typing import Optional
from flask import current_app
from circuitbreaker import circuit
from config import CircuitBreakerPersonalizado
from clients.base_client import BaseClient
import logging

logger = logging.getLogger(__name__)

class NotificationClient(BaseClient):

    def __init__(self, app):
        super().__init__(app, "notification-service")
        self.base_url = app.config.get('NOTIFICATION_SERVICE_URL')
        self.timeout = 5

    @circuit(cls=CircuitBreakerPersonalizado)
    def realizar_notificacion(self):
        """Envía una notificación de acción realizada"""
        try:
            # Introducir la url del post de notificaciones 
            url = f""

            response = self._make_request('POST', url)

            if response.status_code == 404:
                return None
            if response.status_code >= 500:
                logger.error(f"Error al intentar comunicarte con el microservicio de notificaciones {response.status_code}")
                return None

            response.raise_for_status()

            data = response.json()
            return data    

        except requests.exceptions.ConnectionError as e:
            raise Exception("Servicio de contenido no disponible")
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error insertar una notificacion al microservicio")
            return None