from model.order_model_ import Order, OrderItem, OrderStatus
from typing import Optional, Tuple, List
from sqlalchemy import desc
from datetime import datetime
from db import db
import math

class OrderDAO:

    @staticmethod
    def find_by_public_id(public_id: str) -> Optional[Order]:
        """Encontrar un Order con un ID público"""
        try:    
            order = db.session.query(Order).filter_by(public_id = public_id).first()
            return order
        except Exception as e:
            print(f"Error buscando el orden {public_id}: {str(e)}")
            return None
        
    
    @staticmethod
    def find_by_filter(
        seller: Optional[str] = None,
        status: Optional[str] = None,
        dateFrom: Optional[str] = None,
        dateTo: Optional[str] = None,
        page: int = 0,
        size: int = 20
    ) -> Optional[Tuple[List[Order], int, int]]:
        
        baseQuery = Order.query

        """
        Encontrar todas las compras por filtro y paginación

        Retorna: Tupla (orders, total_elementos, total_paginas)
        """
        
        query = OrderDAO._filter_apply_(baseQuery, seller, status, dateFrom, dateTo)

        # CASE: If no filter was applied
        if query is None:
            return None 

        # Obtener todos los elementos obtenidos
        total_elementos = query.count()

        # Aplicar paginación y orden
        orders = query.order_by(desc(Order.created_at))\
                        .offset(size * page) \
                        .limit(size) \
                        .all()
        
        # Calcular total de páginas
        total_paginas = math.ceil(total_elementos / size) if size > 0 else 0

        return orders, total_elementos, total_paginas

    @staticmethod
    def _filter_apply_(
        query,
        seller: Optional[str],
        status: Optional[str],
        dateFrom: Optional[str],
        dateTo: Optional[str]
    ):
           
    
        """ Aplicar filtros a la query """
        # Filtro por vendedor, busca en los items de todas las ordenes realizadas
        if seller:
            try:
                query = Order.query.join(Order.items) \
                    .filter(OrderItem.seller_username == seller)
            except ValueError:
                # Caso en el que el valor de status se meta como una cadena y no se elija
                # En un DEPLOY de opciones disponibles.
                pass
            
        # Filtro por estado de la compra
        if status:
            print(status)
            # Obtenemos el estado del ENUM
            order_status = OrderStatus(status.upper())
            # Filtramos la consulta con el order_status
            query = query.filter(Order.status == order_status)    
        
        # Filtro por fecha de realización de compra
        if dateFrom:
            date_from_obj = datetime.strptime(dateFrom, '%Y-%m-%d').date()
            query = query.filter(Order.created_at >= date_from_obj)

        # Filtro por compras que todavía no han finalizado
        if dateTo:
            date_to_obj = datetime.strptime(dateTo, '%Y-%m-%d').date()
            date_to_end = datetime.combine(date_to_obj, datetime.max.time())
            query = query.filter(Order.created_at <= date_to_end)    

        return query
    
    @staticmethod
    def get_all_no_delivered() -> Optional[List[Order]]:
        
        try:

            orders = Order.query.filter(
                Order.status.in_([OrderStatus.PENDING, OrderStatus.PAID])
            ).all()

            return orders if orders else None

        except Exception as e:
            print(f"Error en get_all_no_delivered: {e}")
            return None    

    @staticmethod
    def mark_order_as_paid(order_id: str) -> Optional[Order]:

        order = OrderDAO.find_by_public_id(order_id)
        if not order:
            raise Exception(f"Order {order_id} no encontrado")

        # Actualizo estado y timestamp de confirmacion
        order.status = OrderStatus.PAID
        order.updated_at = datetime.now()    
        
        db.session.commit()

        # Refrescar el contenido del order actualizado 
        db.session.refresh(order)

        return order
    
    @staticmethod
    def get_all(size: int, page: int) -> Optional[Tuple[List[Order], int, int]]:

        base_query = Order.query

        total_elementos = base_query.count()

        # CASE: No elements in table orders
        if total_elementos == 0:
            return [], total_elementos, 0
        

        orders = Order.query.order_by(desc(Order.created_at))\
                        .offset(size * page) \
                        .limit(size) \
                        .all()
        
        total_pagina = math.ceil(total_elementos / size) if size > 0 else 0

        return orders, total_elementos, total_pagina
    

    @staticmethod
    def get_by_id(order_id: str) -> Optional[Order]:
        return Order.query.filter(Order.public_id == order_id)
    
    @staticmethod
    def add_order(order: Order, username: str) -> Order:
        try:
            order.made_by_username = username
            db.session.add(order)
            db.session.commit()
            return order
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_by_public_id(public_id: str, update_data: dict) -> Optional[Order]:
        try:
            order_encontrado = OrderDAO.find_by_public_id(public_id)
            print(order_encontrado)
            if order_encontrado:
                print(order_encontrado.status)
                if order_encontrado.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
                    raise ValueError(f"La orden {public_id} no se puede actualizar porque tiene status {order_encontrado.status}")
                 
                for key, value in update_data.items():
                    print("Entro")
                    if hasattr(order_encontrado, key):

                        if key == 'status' and isinstance(value, str):
                            setattr(order_encontrado, key, OrderStatus(value.upper()))
                        else:
                            setattr(order_encontrado, key, value)
                db.session.commit()
                return order_encontrado
            return None
        except Exception as e:
            db.session.rollback()
            raise e                

    @staticmethod
    def get_orders_by_seller(seller: str, 
                             page: int=0, 
                             size: int=20) -> Tuple[List[Order], int, int]:
        query = Order.query.join(Order.items) \
                    .filter(OrderItem.seller_username == seller)

        total_elementos = query.count()
        print(total_elementos)

        orders = query.order_by(desc(Order.created_at)) \
                      .offset(size * page) \
                      .limit(size)\
                      .all()
        total_paginas = math.ceil(total_elementos / size) if size > 0 else 0

        return orders, total_elementos, total_paginas