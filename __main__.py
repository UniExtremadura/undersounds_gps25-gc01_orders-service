from flask_sqlalchemy import SQLAlchemy
from utils.encoder import CustomJSONProvider
from dotenv import load_dotenv
from db import db
from controllers.order_controller import order_bp
from sqlalchemy import text
from auth.keycloak_config import init_keycloak
from helpers.db_connection import dbConectar, verify_connection
import os

import connexion

load_dotenv()

def main():
    db_url = os.getenv("DATABASE_URL")
    print(f"🔍 URL de conexión: {db_url}") 
    
    connex_app = connexion.App(__name__, specification_dir='./swagger/')
    connex_app.json = CustomJSONProvider(connex_app)
    connex_app.add_api('swagger.yaml', 
                arguments={'title': 'Servicio de Compras'}, 
                pythonic_params=True,
                validate_responses=True)

    flask_app = connex_app.app

    flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    # Blueprint register
    flask_app.register_blueprint(order_bp, url_prefix='/api/v1')

    # Keycloak app config
    flask_app.config['KEYCLOAK_SERVER_URL'] = 'http://localhost:8081/'
    flask_app.config['KEYCLOAK_CLIENT_ID'] = 'orders-service'
    flask_app.config['KEYCLOAK_REALM'] =    'undersounds'

    # Init keycloak
    init_keycloak(flask_app)
    
    
    db.init_app(flask_app)
    # Verificación de conexión y tablas
    verify_connection(flask_app, db)

    print("Servicio de Compras iniciando en puerto 8084...")

    # FLASK APP RUN
    flask_app.run(port=8084)

    # SWAGGER VALIDATOR APP RUN
    #connex_app.run(port=8084)


if __name__ == '__main__':
    main()
    