import pytest
import requests
from unittest.mock import Mock, patch
from clients.user_client import UserClient

class TestUserClient:

    @patch('clients.base_client.requests.request')
    @patch('clients.base_client.KeycloakService')
    def test_get_seller_by_username_success(self, mock_keycloak_class, mock_request):
        """Test obtener vendedor exitosamente"""
        mock_app = Mock()
        mock_app.config = {'USERS_SERVICE_URL': 'http://users-service:5001'}
        
        mock_keycloak = Mock()
        mock_keycloak._get_token.return_value = "mock-jwt-token"
        mock_keycloak_class.return_value = mock_keycloak
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "username": "test_user",
            "name": "Test User",
            "email": "test@example.com"
        }
        mock_request.return_value = mock_response
        
        # Ejecutar test
        client = UserClient(mock_app)
        result = client.get_seller_by_username("test_user")
        
        assert result['username'] == "test_user"
        assert result['name'] == "Test User"

    @patch('clients.base_client.requests.request')
    @patch('clients.base_client.KeycloakService')
    def test_get_user_by_username_not_found(self, mock_keycloak_class, mock_request):
        """Test cuando usuario no existe"""
        mock_app = Mock()
        mock_app.config = {'USERS_SERVICE_URL': 'http://users-service:5001'}
        
        mock_keycloak = Mock()
        mock_keycloak._get_token.return_value = "mock-jwt-token"
        mock_keycloak_class.return_value = mock_keycloak
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        
        client = UserClient(mock_app)
        result = client.get_seller_by_username("usuario_inexistente")
        print(result)
        assert result is None