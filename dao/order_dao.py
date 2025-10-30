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