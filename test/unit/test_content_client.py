from unittest.mock import Mock, patch
from clients.content_client import ContentClient


class TestContentClient:
    
    @patch('clients.base_client.requests.request')
    @patch('clients.base_client.KeycloakService')
    def test_get_product_by_id_success(self, mock_keycloak_class, mock_request_get):
        # Configuro del mock request
        mock_app = Mock()
        mock_app.config = {'CONTENT_SERVICE_URL': 'http://content-service'}
        
        mock_keycloak = Mock()
        mock_keycloak._get_token.return_value = "mock-token"
        mock_keycloak_class.return_value = mock_keycloak
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value=  {
            "success": True,
            "data": {
                "id": "1255a990-0608-481f-afb2-cc685e65a3ce",
                "name": "test-product",
                "description": "esto es una prueba",
                "price": 19.99,
                "stock": 100,
                "images": [
                    "https://cdn.example.com/products/img1.jpg",
                    "https://cdn.example.com/products/img2.jpg"
                ],
                "artist": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "The Beatles",
                    "profilePicture": "https://cdn.example.com/artists/beatles.jpg"
                },
                "createdAt": "2025-11-04T10:15:30"
            }
        }

        mock_request_get.return_value = mock_response

        # Ejecución
        client = ContentClient(mock_app)
        result = client.get_product_by_id("1255a990-0608-481f-afb2-cc685e65a3ce")
        print(result)
        assert result is not None
        assert result.get('name') == "test-product"
        assert result.get('price') == 19.99

    @patch('clients.base_client.requests.request')
    @patch('clients.base_client.KeycloakService')
    def test_get_product_by_id_not_found(self, mock_keycloak_class, mock_get_product):
        """Test de producto no encontrado"""
        mock_app = Mock()
        mock_app.config = {'CONTENT_SERVICE_URL': 'http://content-service'}

        mock_keycloak = Mock()
        mock_keycloak._get_token.return_value = "mock-token"
        mock_keycloak_class.return_value = mock_keycloak

        mock_response = Mock()
        mock_response.status_code = 404
        mock_get_product.return_value = mock_response

        #Ejecución
        client = ContentClient(mock_app)
        result = client.get_product_by_id("1255a990-0608-481f-afb2-cc685e65a3ce")

        assert result is None

    @patch('clients.base_client.requests.request')
    @patch('clients.base_client.KeycloakService')
    def test_get_product_stock_by_id(self, mock_keycloak_class, mock_request):
        """Test para obtener exitosamente el stock de un producto""" 
        mock_app = Mock()
        mock_app.config = {'CONTENT_SERVICE_URL': 'http://content-service'}
        
        mock_keycloak = Mock()
        mock_keycloak._get_token.return_value = "mock-token"
        mock_keycloak_class.return_value = mock_keycloak

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {
                'stock': 50,
            }
        }

        mock_request.return_value = mock_response

        client = ContentClient(mock_app)
        result = client.get_product_stock_by_id("prod-123")
        assert result is not None
        assert result['success'] is True
        assert result['stock_product'] == 50

    @patch('clients.base_client.requests.request')
    @patch('clients.base_client.KeycloakService')
    def test_get_songs_by_id_success(self, mock_keycloak_class, mock_request_get):
        """Test de obtencion de una cancion por su id"""
        mock_app = Mock()
        mock_app.config = {'CONTENT_SERVICE_URL': 'http://content-service'}

        mock_keycloak = Mock()
        mock_keycloak._get_token.return_value = "mock-token"
        mock_keycloak_class.return_value = mock_keycloak

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "id": "987e6543-e21b-12d3-a456-426614174111",
                "name": "Hey Jude",
                "cover": "https://cdn.example.com/songs/heyjude.jpg",
                "genres": ["ROCK", "POP"],
                "description": "Canción clásica del álbum Abbey Road de The Beatles.",
                "duration": 420,
                "previewStart": 60,
                "previewDuration": 30,
                "price": 1.29,
                "artist": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "The Beatles",
                    "profilePicture": "https://cdn.example.com/artists/beatles.jpg"
                },
                "album": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Greatest Hits",
                    "cover": "https://cdn.example.com/albums/cover123.jpg"
                },
                "createdAt": "2025-11-04T10:15:30"
            }
        }

        mock_request_get.return_value = mock_response

        #Ejecución
        client = ContentClient(mock_app)
        result = client.get_songs_by_id("987e6543-e21b-12d3-a456-426614174111")
        
        assert result['name'] == "Hey Jude"

    @patch('clients.base_client.requests.request')
    @patch('clients.base_client.KeycloakService')
    def test_get_album_by_id_success(self, mock_keycloak_class, mock_request_get):
        """Test para comprobar la obtención de un album por su id"""
        mock_app = Mock()
        mock_app.config = {'CONTENT_SERVICE_URL': 'http://content-service'}

        mock_keycloak = Mock()
        mock_keycloak._get_token.return_value = "mock-token"
        mock_keycloak_class.return_vale = mock_keycloak

        mock_response = Mock()
        mock_response.status_code = 200    
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Greatest Hits",
                "cover": "https://cdn.example.com/albums/cover123.jpg",
                "durationSeconds": 3600,
                "price": 9.99,
                "description": "Este álbum recopila los mayores éxitos de la carrera del artista.",
                "createdAt": "2025-11-04T10:15:30",
                "artist": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "The Beatles",
                    "profilePicture": "https://cdn.example.com/artists/beatles.jpg"
                },
                "songs": {
                    "id": "987e6543-e21b-12d3-a456-426614174111",
                    "name": "Hey Jude",
                    "durationSeconds": 420,
                    "cover": "https://cdn.example.com/songs/heyjude.jpg"
                }
            }
        }

        mock_request_get.return_value = mock_response

        # Ejecución
        client = ContentClient(mock_app)
        result = client.get_albums_by_id("550e8400-e29b-41d4-a716-446655440000")

        assert result is not None
        assert result['name'] == "Greatest Hits"
        assert result['price'] == 9.99