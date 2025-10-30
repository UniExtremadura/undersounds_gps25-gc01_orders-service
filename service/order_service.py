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
    def generate_public_id() -> str:
        id = uuid.uuid1()
        return str(id)

    @staticmethod
    def list_orders(size: int, page: int):
        return OrderDAO.get_all(size, page)
    

