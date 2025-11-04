from model.order_model_ import Order, OrderItem, OrderStatus
from dao.order_dao import OrderDAO
from dto.order_dto import CreateOrderRequestDTO
from datetime import datetime
#from helpers import ProductNotFoundException
import uuid


class ProductNotFoundException(Exception):
    def __init__(self, campo, mensaje):
        self.campo = campo
        self.mensaje = mensaje
        super().__init__(f"Error en '{campo}': {mensaje}")

class OrderService:

    @staticmethod
    def order_to_dict(order: Order) -> dict:
        """Convert an Order model into a dict"""
        return {
            "publicId": order.public_id,
            "madeBy": {
                "name": order.made_by_username,
                "username": order.made_by_username
            },
            "items": [OrderService.order_item_to_dict(item) for item in order.items],
            "createdAt": order.created_at.isoformat() if order.created_at else None,
            "status": order.status,
            "total": float(order.total) if order.total else sum(item.quantity * item.price for item in order.items)
        }
    
    @staticmethod
    def order_item_to_dict(item: OrderItem) -> dict:
        """Convert an OrderItem model into a dict"""
        return {
            "publicId": item.product_public_id,
            "name": item.product_name,
            "imageSrc": item.product_image_src or "",
            "description": item.product_description or "",
            "seller": {
                "name": item.seller_name,
                "username": item.seller_username,
                "pfp": item.seller_pfp or ""
            },
            "quantity": item.quantity,
            "price": float(item.price),
            "total": float(item.quantity * item.price)
        }
    
    @staticmethod
    def generate_public_id() -> str:
        id = uuid.uuid1()
        return str(id)

    @staticmethod
    def list_orders(size: int, page: int):
        return OrderDAO.get_all(size, page)
    
    @staticmethod
    def list_orders_with_filters(filtros):
        return OrderDAO.find_by_filter(**filtros) # Unpack filtros' dictionary elements to pass them to args of the function
    
    @staticmethod
    def is_order_updatable(orderId: str) -> bool:
        
        order_updatable = OrderDAO.find_by_public_id(orderId)

        if not order_updatable:
            return False

        return order_updatable.status in [OrderStatus.PENDING, OrderStatus.PAID]
    
    @staticmethod
    def update_order(order_id: str, update_data: dict):

        if not OrderService.is_order_updatable(order_id):
            return None

        print("Puedo")
        return OrderDAO.update_by_public_id(order_id, update_data)
    

