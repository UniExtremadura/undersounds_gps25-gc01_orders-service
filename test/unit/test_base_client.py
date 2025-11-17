# tests/unit/test_base_client.py
import pytest
from unittest.mock import Mock, patch
from clients.base_client import BaseClient

class TestBaseClient:
    
    def test_base_client_initialization(self):
        """Test que BaseClient se inicializa correctamente"""
        mock_app = Mock()
        mock_app.config = {
            'KEYCLOAK_SERVER_URL': 'http://keycloak:8081',
            'KEYCLOAK_REALM': 'master',
            'KEYCLOAK_MICROSERVICE_CLIENT_ID': 'microservices',
            'KEYCLOAK_MICROSERVICE_CLIENT_SECRET': 'test-secret'
        }
        
        client = BaseClient(mock_app, "TEST-SERVICE")
        
        assert client.service_name == "TEST-SERVICE"
        assert client.timeout == 10
        assert client.app == mock_app
        assert client._token is None

    @patch('clients.base_client.requests.request')
    @patch('clients.base_client.KeycloakService')
    def test_make_request_with_token(self, mock_keycloak_class, mock_request):
        """Test que _make_request incluye el token JWT"""
        # Configurar mocks
        mock_app = Mock()
        mock_app.config = {'KEYCLOAK_SERVER_URL': 'http://test'}
        
        mock_keycloak = Mock()
        mock_keycloak._get_token.return_value = "mock-jwt-token"
        mock_keycloak_class.return_value = mock_keycloak
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        # Crear client y hacer request
        client = BaseClient(mock_app, "TEST-SERVICE")
        response = client._make_request('GET', 'http://test-service/api/test')
        
        # Verificar que se incluyó el token
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        headers = call_args[1]['headers']
        assert headers['Authorization'] == 'Bearer mock-jwt-token'
        assert headers['X-Service-Name'] == "TEST-SERVICE"
        assert response.status_code == 200

    @patch('clients.base_client.requests.request')
    @patch('clients.base_client.KeycloakService')
    def test_make_request_token_refresh_on_401(self, mock_keycloak_class, mock_request):
        """Test en el que el token se refresca automaticamente al producirse 401"""
        mock_app = Mock()
        mock_app.config = {'KEYCLOAK_SERVER_URL': 'http://test'}

        mock_keycloak = Mock()
        mock_keycloak._get_token.return_value = "old_token"
        mock_keycloak._refresh_token.return_value = "new_token"
        mock_keycloak_class.return_value = mock_keycloak

        # Primera respuesta 401
        mock_response_401 = Mock()
        mock_response_401.status_code = 401

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"success": True}

        mock_request.side_effect = [mock_response_401, mock_response_200]

        client = BaseClient(mock_app, "TEST-SERVICE")
        response = client._make_request('GET', 'http://tist-service/api/test')
        print(f"Respuesta: {response}")
        # Verificar que se hicieron 2 llamadas
        assert mock_request.call_count == 2
        # Verificar que se refrescó el token
        mock_keycloak._get_token.assert_called_once()
        assert response.status_code == 200