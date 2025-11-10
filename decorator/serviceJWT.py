from functools import wraps
from flask import request, jsonify, current_app
from auth.keycloak_service import KeycloakService
import logging

logger = logging.getLogger(__name__)

def service_jwt_required(f):
    """Decorador para validar JWT de microservicios"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token requerido'}), 401
        
        try:
            token = auth_header.split(" ")[1]
            keycloak_service = KeycloakService()

            token_info = keycloak_service.validate_token(token)
            if not token_info:
                return jsonify({'error': 'Token inválido'}), 401
            
            # Verifico que el token es de un microservicio
            if not token_info.get('clientId') == current_app.config.get('KEYCLOAK_CLIENT_ID'):
                return jsonify({'error': 'Token no válido para servicios'}), 403
            
            # Verifico los roles
            roles = token_info.get('realm_access', {}).get('roles', [])
            if 'ROLE_INTERNAL_SERVICE' not in roles:
                return jsonify({'error': 'Permisos insuficientes'}), 403
            
        except Exception as e:
            return jsonify({'error': 'No autorizado'}), 401    

        return f(*args, **kwargs)

    return decorated_function   
