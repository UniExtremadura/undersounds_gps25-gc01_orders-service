from model.order_model_ import Order, OrderItem, OrderStatus
from typing import Optional, Tuple, List
from sqlalchemy import desc
import datetime
from db import db
import math

class OrderDAO:
    
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