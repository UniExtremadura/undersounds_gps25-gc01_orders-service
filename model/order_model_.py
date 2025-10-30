
from flask_sqlalchemy import SQLAlchemy
from db import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import enum
from datetime import datetime

class OrderStatus(enum.Enum):
    PENDING = "PENDING",
    PAID = "PAID",
    SHIPPED = "SHIPPED",
    CANCELLED = "CANCELLED"

class Order(db.Model):
    # Definicion del nombre de la tabla, si no se incluye, coge el nombre de la clase en formato snake-case para la creación de la tabla
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique = True, nullable = False, index = True)
    made_by_username = db.Column(db.String(50), nullable = False, index = True)
    status = db.Column(db.Enum(OrderStatus), default = OrderStatus.PENDING, nullable = False)
    total = db.Column(db.Float, nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now, nullable = False)
    updated_at = db.Column(db.DateTime, default = datetime.now, onupdate = datetime.now, nullable = True)

    # Relación ONE-TO-MANY con la tabla Items
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="joined")

    def __repr__(self):
        return f"<Order {self.public_id} - {self.status}>"
    
class OrderItem(db.Model):
    
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, ForeignKey('orders.id'), nullable=False)

    #Información del producto (contenido)
    product_public_id = db.Column(db.String(36), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_image_src = db.Column(db.String(500))
    product_description = db.Column(db.String(500))


    # Información del vendedor
    seller_username = db.Column(db.String(50), nullable=False)
    seller_name = db.Column(db.String(200), nullable=False)
    seller_pfp = db.Column(db.String(500))
    # Información del precio y la cantidad
    price = db.Column(db.Integer, nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    total = db.Column(db.Integer, nullable = False)

    order = relationship("Order", back_populates="items")

    def __repr__(self):
       return f"<OrderItem {self.product_name} x {self.product_quantity}>"

