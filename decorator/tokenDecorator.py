from functools import wraps
from flask import request, jsonify
from keycloak import KeycloakOpenID
from auth.keycloak_config import get_keycloak_openid

keycloak_openId: KeycloakOpenID = get_keycloak_openid # Get the openId configured of keycloak

# Decorator used to protect endpoints with JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization') # Get the Authorization content of header request
        if not auth_header: # Not authorized
            return jsonify({"error": "Token requerido para realizar la operacion"}), 401
        
        try:
            token = auth_header.split(" ")[1] # Get Bearer Auth content
            user_info = keycloak_openId.userinfo(token) # Validate token with Keycloak DB
            if user_info:
                pass
            else:
                return jsonify({'error': 'Usuario no autenticado'})
            # IF NO ERROR -> VALID TOKEN
        except Exception as e:
            return jsonify({'error': 'Token invalido'}), 401    
        
        return f(*args, **kwargs)
    
    return decorated