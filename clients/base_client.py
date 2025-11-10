# clients/base_client.py
import requests
from flask import current_app
from auth.keycloak_service import KeycloakService
from typing import Optional
import logging
from threading import Lock

logger = logging.getLogger(__name__)

class BaseClient:
    def __init__(self, app, service_name: str):
        self.app = app
        self.service_name = service_name
        self.timeout = 10
        self.keycloak_service = KeycloakService(app)
        self._token = None
        self._token_lock = Lock()
    
    def _get_token(self) -> Optional[str]:
        """Obtener token JWT (con cache simple)"""
        with self._token_lock:
            if not self._token:
                self._token = self.keycloak_service._get_token()
            return self._token
    
    def _refresh_token(self):
        """Forzar refresh del token"""
        with self._token_lock:
            self._token = self.keycloak_service.get_service_token()
    
    def _get_headers(self) -> dict:
        """Headers con JWT para requests a otros microservicios"""
        token = self._get_token()
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'{self.service_name}/1.0.0',
            'X-Service-Name': f'{self.service_name}'
        }
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        return headers
    
    def _make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Realizar request con manejo de token"""
        headers = self._get_headers()

        try:

            response = requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                headers=headers,
                **kwargs
            )
            
            # Si el token expiró (401), refrescar y reintentar
            if response.status_code == 401:
                logger.info("Token expirado, refrescando...")
                self._refresh_token()
                headers = self._get_headers()
                response = requests.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    headers=headers,
                    **kwargs
                )
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en request a {url}: {e}")
            return None