from functools import wraps
from auth.keycloak_config import keycloak_openid
from flask import request, jsonify

def role_validator(*required_role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization').split(" ")[1]

            # GET role from token
            token_info = keycloak_openid.introspect(token)
            user_role = token_info.get('realm_access', {}).get('roles', [])

            # Verify user roles
            if not any(role in user_role for role in required_role):
                return jsonify({'error': 'Permisos no autorizados'}), 403
            
            return f(*args, **kwargs)
        return decorated    
    return decorator