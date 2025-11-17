import pytest
from flask import Flask
from controllers.order_controller import order_bp

@pytest.fixture
def app():
    """Crear aplicación Flask para testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(order_bp)
    return app

@pytest.fixture
def client(app):
    """Crear cliente de testing"""
    return app.test_client()