import pytest
from unittest.mock import Mock, patch
from service.order_service import OrderService, ProductNotFoundException
from dto.order_dto import CreateOrderRequestDTO, CreateOrderItemRequestDTO
from models.order_model_ import OrderItem, OrderStatus

""" USO DE PATCH"""
#  Simulan componentes en funcionamiento pero en realidad no lo están
"""@patch('service.order_service.OrderDAO')"""
# Por qué: OrderService.save() llama a OrderDAO.add_order()
# Qué hace: Evita que se conecte a la base de datos real
# Qué simula: El guardado en base de datos
"""@patch('service.order_service.user_client')"""
# Por qué: OrderService.save() llama a user_client.get_seller_by_username()
# Qué hace: Evita llamadas HTTP reales al servicio de usuarios
# Qué simula: La respuesta del microservicio de usuarios
"""@patch('service.order_service.content_client')"""
# Por qué: OrderService.save() llama a content_client.get_product_by_id()
# Qué hace: Evita llamadas HTTP reales al servicio de contenido
# Qué simula: La respuesta del microservicio de contenido

class TestOrderService:

    @patch('service.order_service.OrderDAO')
    @patch('service.order_service.user_client')
    @patch('service.order_service.content_client')
    def test_create_order_success(self, mock_content_client, mock_user_client, mock_order_dao):
        """Test creación exitosa para el order_service"""
        
        # Configurar mocks de clients
        mock_user_client.get_seller_by_username.return_value = {
            "username": "test_user",
            "artisticName": "Test User",
        }
        
        mock_content_client.get_product_by_id.return_value = {
            "price": 15.99,
            "product_name": "Álbum de Música",
            "product_image_src": "album.jpg",
            "product_description": "Un álbum increíble",
            "artist": {
                "username": "artista_famoso",
                "artisticName": "Artista Famoso",
                "pfp": "artist.jpg"
            }
        }
        
        # Mock del OrderDAO.add_order para devolver una orden simulada
        mock_order = Mock()
        mock_order.public_id = "order_123"
        mock_order.total = 31.98
        mock_order_dao.add_order.return_value = mock_order
        
        # Crear datos de prueba
        order_items = [CreateOrderItemRequestDTO(
            productId="prod_123",
            quantity=2
        )]
        order_dto = CreateOrderRequestDTO(items=order_items)
        
        # Ejecutar
        result = OrderService.save(order_dto, "test_user")
        
        # Verificar
        mock_user_client.get_seller_by_username.assert_called_once_with("test_user")
        mock_content_client.get_product_by_id.assert_called_once_with("prod_123")
        mock_order_dao.add_order.assert_called_once()
        assert result.total == 31.98

    @patch('service.order_service.OrderDAO')
    @patch('service.order_service.user_client')
    @patch('service.order_service.content_client')
    def test_create_order_user_not_found(self, mock_content_client, mock_user_client, mock_order_dao):
        """Test cuando usuario no existe"""
        mock_user_client.get_seller_by_username.return_value = None
        
        order_items = [CreateOrderItemRequestDTO(productId="prod_123", quantity=1)]
        order_dto = CreateOrderRequestDTO(items=order_items)
        
        with pytest.raises(ValueError, match="usuario test_user no encontrado"):
            OrderService.save(order_dto, "test_user")
        
        # Verificar que NO se llamó al DAO
        mock_order_dao.add_order.assert_not_called()

    @patch('service.order_service.OrderDAO')
    @patch('service.order_service.user_client')
    @patch('service.order_service.content_client')
    def test_create_order_product_not_found(self, mock_content_client, mock_user_client, mock_order_dao):
        """Test cuando producto no existe"""
        mock_user_client.get_seller_by_username.return_value = {
            "username": "test_user", "name": "Test User"
        }
        mock_content_client.get_product_by_id.return_value = None
        
        order_items = [CreateOrderItemRequestDTO(productId="prod_inexistente", quantity=1)]
        order_dto = CreateOrderRequestDTO(items=order_items)
        
        with pytest.raises(ProductNotFoundException):
            OrderService.save(order_dto, "test_user")
        
        # Verificar que NO se llamó al DAO
        mock_order_dao.add_order.assert_not_called()

    @patch('service.order_service.OrderDAO')
    @patch('service.order_service.content_client')
    def test_check_stock_availability_success(self, mock_content_client, mock_order_dao):
        """Test verificación stock exitosa"""    

        mock_item = Mock(spec=OrderItem)
        mock_item.product_public_id = "prod-123"
        mock_item.quantity = 2
        mock_order = Mock()
        mock_order.items = [mock_item]

        mock_order_dao.find_by_public_id.return_value = mock_order

        mock_content_client.get_product_stock_by_id.return_value = {
            'success': True,
            'stock_product': 50
        }

        result = OrderService.check_stock_availability("order-123")
        assert result['all_available'] is True
        assert len(result['details']) == 1
        assert result['details'][0]['available'] is True

    @patch('service.order_service.OrderDAO')
    @patch('service.order_service.content_client')
    def test_check_stock_availability_inssuficient(self, mock_content_client, mock_order_dao):
        """Test verificación insuficiencia de stock"""

        mock_item = Mock(spec=OrderItem)
        mock_item.product_public_id = "prod-123"
        mock_item.quantity = 101
        mock_order = Mock()
        mock_order.items = [mock_item]

        mock_order_dao.find_by_public_id.return_value = mock_order

        mock_content_client.get_product_stock_by_id.return_value = {
            'succes': True,
            'stock_product': 50
        }

        result = OrderService.check_stock_availability("order-123")
        assert result['all_available'] is False
        assert len(result['details']) == 1
        
    @patch('service.order_service.OrderDAO')
    @patch('service.order_service.payment_client')
    def test_process_order_payment_success(self, mock_payment_client, mock_order_dao):
        """Test procesamiento de pagos exitoso"""
        
        # 1. Mock de la orden
        mock_order = Mock()
        mock_order.public_id = "order-123"    
        mock_order.total = 50.0
        mock_order.status = OrderStatus.PENDING

        # 2. Configurar DAO
        mock_order_dao.find_by_public_id.return_value = mock_order
        mock_order_dao.mark_order_as_paid.return_value = mock_order

        # 3. Configurar payment_client - SI ES UNA INSTANCIA
        # El mock ya representa la instancia, solo configura el método
        mock_payment_client.procesamiento_pagos.return_value = {
            'success': True,
            'payment_id': 'payment_123',
            'status': 'COMPLETED'
        }

        order_data = {
            'public_id': 'order-123',
            'made_by_username': 'antonio',
            'quantity': 2,
            'payment_method': 'PLATFORM_BALANCE',
            'status': 'PAID'
        }

        # 4. Ejecutar
        result = OrderService.process_order_payment("order-123", order_data)
        
        # 5. Aserciones
        assert result['success'] is True
        assert result['payment_id'] == 'payment_123'
        mock_payment_client.procesamiento_pagos.assert_called_once_with(order_data)