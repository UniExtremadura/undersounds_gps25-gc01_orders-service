from keycloak import KeycloakOpenID

keycloak_openid = None

def init_keycloak(app):
    global keycloak_openid
    keycloak_openid = KeycloakOpenID(
        server_url = app.config['KEYCLOAK_SERVER_URL'],
        client_id = app.config['KEYCLOAK_CLIENT_ID'],
        realm_name = app.config['KEYCLOAK_REALM'],
        client_secret_key = app.config['KEYCLOAK_CLIENT_SECRET'] 
    )

def get_keycloak_openid():
    return keycloak_openid    