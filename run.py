from init import create_app
from config import config
from helpers.db_connection import verify_connection
from db import db
import os

def main():
    # Create application
    app = create_app()
    
    # Verify conexion to the DB
    with app.app_context():
        verify_connection(app, db)
    
    # Initial info
    print("🚀 Servicio de Compras iniciado")
    print(f"📚 Entorno: {os.getenv('FLASK_ENV', 'development')}")
    print(f"🌐 URL: http://localhost:5000")
    print(f"📖 Documentación: http://localhost:5000/api/v1/ui/")
    print(f"❤️  Health Check: http://localhost:5000/api/v1/health")
    
    # Ejecutar aplicación
    app.run(host='0.0.0.0', port=5000, debug=config['development'])

if __name__ == '__main__':
    main()