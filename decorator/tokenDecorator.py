from functools import wraps
from flask import request, jsonify, current_app
from jose import jwt
from jose.backends import RSAKey
from jose.utils import base64url_decode
import requests
import json

# Cache para JWKS
_jwks_cache = None

def get_jwks_keys():
    """
    Obtiene las claves JWKS de Keycloak
    """
    global _jwks_cache
    if _jwks_cache is None:
        try:
            keycloak_url = current_app.config.get('KEYCLOAK_SERVER_URL', 'http://keycloak:8080')
            realm = current_app.config.get('KEYCLOAK_REALM', 'undersounds')
            
            jwks_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/certs"
            current_app.logger.info(f"Obteniendo JWKS desde: {jwks_url}")
            
            response = requests.get(jwks_url, timeout=10)
            response.raise_for_status()
            _jwks_cache = response.json()
            current_app.logger.info("JWKS obtenido correctamente")
        except Exception as e:
            current_app.logger.error(f"Error obteniendo JWKS: {e}")
            raise Exception(f"No se puede obtener JWKS: {str(e)}")
    
    return _jwks_cache

def get_public_key(token, jwks):
    """
    Obtiene la clave pública correcta para verificar el token
    """
    try:
        # Obtener el header del token sin verificar
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        
        current_app.logger.info(f"Buscando clave para kid: {kid}")
        
        if not kid:
            raise Exception("Token no contiene kid en el header")
        
        # Buscar la clave correspondiente
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                current_app.logger.info(f"Clave encontrada para kid: {kid}")
                return key
        
        raise Exception(f"No se encontró clave pública para kid: {kid}. Claves disponibles: {[k.get('kid') for k in jwks.get('keys', [])]}")
    
    except Exception as e:
        current_app.logger.error(f"Error obteniendo public key: {e}")
        raise

def token_required(roles: list = None):
    """
    Decorador para proteger endpoints con JWT
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            current_app.logger.info("Verificando token...")
            
            if not auth_header:
                return jsonify({'code': 401, 'message': 'Token requerido'}), 401
            
            try:
                # Verificar formato
                if not auth_header.startswith('Bearer '):
                    return jsonify({'message': 'Formato inválido. Usa: Bearer <token>'}), 401
                
                token = auth_header.split(" ")[1]
                
                # Obtener configuración
                #keycloak_url = current_app.config.get('KEYCLOAK_SERVER_URL', 'http://localhost:8090')
                #realm = current_app.config.get('KEYCLOAK_REALM', 'undersounds')
                client_id = current_app.config.get('KEYCLOAK_CLIENT_ID', 'orders-service')
                
                current_app.logger.info(f"Verificando token para client: {client_id}")
                
                # Obtener JWKS
                jwks = get_jwks_keys()
                
                # Obtener clave pública específica
                public_key = get_public_key(token, jwks)
                
                # Decodificar y verificar JWT
                current_app.logger.info("Decodificando token...")
                claims = jwt.decode(
                    token=token,
                    key=public_key,
                    algorithms=['RS256'],
                    audience=client_id,
                    options={
                        "verify_aud": True, 
                        "verify_exp": True,
                        "verify_iss": True,
                        "verify_signature": True
                    }
                )
                
                current_app.logger.info(f"Token válido para usuario: {claims.get('username', 'Unknown')}")
                current_app.logger.info(f"Roles en token: {claims.get('roles', [])}")
                
                # Validar roles si se especificaron
                if roles:
                    token_roles = claims.get('roles', [])
                    if not any(role in token_roles for role in roles):
                        return jsonify({
                            'message': 'Roles insuficientes',
                            'required': roles,
                            'user_roles': token_roles
                        }), 403
                
                # Guardar claims para usar en el endpoint
                request.user_claims = claims
                
            except jwt.ExpiredSignatureError:
                current_app.logger.warning("Token expirado")
                return jsonify({'message': 'Token expirado'}), 401
            except jwt.JWTClaimsError as e:
                current_app.logger.warning(f"Error en claims del token: {e}")
                return jsonify({'message': f'Token inválido: {str(e)}'}), 401
            except Exception as e:
                current_app.logger.error(f"Error verificando token: {str(e)}")
                return jsonify({'error': 'No autorizado', 'details': str(e)}), 401
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator