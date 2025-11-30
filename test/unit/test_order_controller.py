import pytest
from unittest.mock import patch, Mock

class TestOrderController:

    @patch('controllers.order_controller.order_service.OrderService')
    def test_get_order_success(self, mock_order_service, client):
        # Mockear order_to_dict para que retorne un dict válido
        mock_order_service.order_to_dict.return_value = {
            "publicId": "order1",
            "madeBy": {
                "name": "Test User",
                "username": "test_user"
            },
            "items": [],
            "createdAt": "2024-01-01T00:00:00Z",
            "status": "PENDING",
            "total": 99.99
        }
        
        # También mockear find_order para retornar algo
        mock_order = Mock()
        mock_order_service.find_order.return_value = mock_order

        response = client.get('/orders/order1')

        assert response.status_code == 200
        mock_order_service.find_order.assert_called_once_with("order1")
        mock_order_service.order_to_dict.assert_called_once_with(mock_order)