import yaml
from flask import jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime
from helpers.ApiExceptions import APIException
from flask import request

def register_blueprints(app):
    """Registry all app's blueprints"""
    from controllers.order_controller import order_bp
    
    # Registry endpoints paths
    app.register_blueprint(order_bp, url_prefix='/api/v1')
    
    # Registry basic paths
    register_basic_routes(app)

def register_swagger(app):
    """Configure and registry Swagger UI"""
    swaggerui_blueprint = get_swaggerui_blueprint(
        app.config['SWAGGER_URL'],
        app.config['API_URL'],
        config={
            'app_name': app.config['SERVICE_NAME'],
            'docExpansion': 'none'
        }
    )
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=app.config['SWAGGER_URL'])
    
    # Endpoint to serve openapi.json
    @app.route(app.config['API_URL'])
    def serve_swagger_json():
        try:
            with open('./swagger/swagger.yaml', 'r', encoding='utf-8') as file:
                swagger_spec = yaml.safe_load(file)
            return jsonify(swagger_spec)
        except Exception as e:
            app.logger.error(f"Error cargando swagger.yaml: {e}")
            return jsonify({
                "error": "No se pudo cargar la especificación Swagger",
                "details": str(e)
            }), 500

def register_basic_routes(app):
    """Registra basic app's paths"""
    
    @app.route('/')
    def index():
        return jsonify({
            "service": app.config['SERVICE_NAME'],
            "version": app.config['SERVICE_VERSION'],
            "status": "running",
            "endpoints-generales": {
                "docs": app.config['SWAGGER_URL'],
                "health": "/api/v1/health"
            }
        })
    
    @app.route('/api/v1/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": app.config['SERVICE_NAME'],
            "timestamp": datetime.today()
        })
    
    # Manejador global de excepciones de tipo APIException, les da el formato de JSON para devolverlo
    @app.errorhandler(APIException)
    def handle_api_exception(e):
        response = {
            "error": e.error,
            "message": e.message,
            "status": e.status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": request.path
        }
        return jsonify(response), e.status  
    
    # Manejador global de excepciones con estado 500, les da el formato de JSON para devolverlo
    @app.errorhandler(500)
    def handle_internal_server_error(e):
        response = {
            "error": "Internal Server Error",
            "message": str(e) if str(e) else "Ha ocurrido un error inesperado",
            "status": 500,
            "path": request.path,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        return jsonify(response), 500