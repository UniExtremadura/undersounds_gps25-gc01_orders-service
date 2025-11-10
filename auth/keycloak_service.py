import requests
from flask import current_app
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class KeycloakService:
    def __init__(self, app):
        self.server_url = app.config.get('KEYCLOAK_SERVER_URL')
        self.realm = app.config.get('KEYCLOAK_REALM')
        self.client_id = app.config.get('KEYCLOAK_CLIENT_ID')
        self.client_secret = app.config.get('KEYCLOAK_CLIENT_SECRET')

    def _get_token(self) -> Optional[Dict]:
        try:
            token_url = f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/token"
            
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(
                token_url,
                data=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            token_data = response.json()
            return token_data['access_token']
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo token de Keycloak: {e}")
            return None    
        
    def validate_token(self, token: str) -> Optional[Dict]:
        """Validar JWT token"""
        try:
            introspect_url = f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/token/introspect"
            
            payload = {
                'token': token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(
                introspect_url,
                data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=5
            )
            response.raise_for_status()
            
            token_info = response.json()
            return token_info if token_info.get('active') else None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error validando token: {e}")
            return None    