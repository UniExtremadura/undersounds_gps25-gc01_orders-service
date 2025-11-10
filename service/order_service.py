from model.order_model_ import Order, OrderItem, OrderStatus
from dao.order_dao import OrderDAO
from dto.order_dto import CreateOrderRequestDTO
from typing import Optional, List
from datetime import datetime, UTC
from clients import user_client, content_client, payment_client
#from helpers import ProductNotFoundException
import uuid
import logging

logger = logging.getLogger(__name__)

class ProductNotFoundException(Exception):
    def __init__(self, campo, mensaje):
        self.campo = campo
        self.mensaje = mensaje
        super().__init__(f"Error en '{campo}': {mensaje}")

class OrderNotFoundException(Exception):
    pass

class PaymentProcessingException(Exception):
    pass


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
    def find_order(order_id: str):
        return OrderDAO.find_by_public_id(order_id)
    
    @staticmethod
    def generate_public_id() -> str:
        id = uuid.uuid1()
        return str(id)
    
    @staticmethod
    def find_order_by_public_id(order_id: str):
        return OrderDAO.find_by_public_id(order_id)
    
    @staticmethod
    def update_order(order_id: str, update_data: dict):

        if not OrderService.is_order_updatable(order_id):
            return None

        print("Puedo")
        return OrderDAO.update_by_public_id(order_id, update_data)
    
    @staticmethod
    def is_order_updatable(orderId: str) -> bool:
        
        order_updatable = OrderDAO.find_by_public_id(orderId)

        if not order_updatable:
            return False

        return order_updatable.status in [OrderStatus.PENDING, OrderStatus.PAID]
    
    @staticmethod
    def is_order_confirm(orderId: str) -> bool:

        order_confirm = OrderDAO.find_by_public_id(orderId)

        if not order_confirm:
            return False
        
        return order_confirm.status is OrderStatus.PENDING
    
    @staticmethod
    def check_stock_availability(order_id: str) -> dict:
        """
        Verifica la disponibilidad de stock antes de procesar el pago
        """
        try:
            order = OrderService.find_order(order_id)
            if not order:
                raise OrderNotFoundException(f"Orden {order_id} no encontrada")
            
            availability_check = []
            
            for item in order.items:
                
                try:

                    stock_response = content_client.get_product_stock_by_id(item.product_public_id)
                    if not stock_response or not stock_response.get('success') is True:
                        availability_check.append({
                            'product_id': item.product_public_id,
                            'available': False,
                            'error': 'Servicio de contenido no disponible'
                        })
                        continue
                    
                    current_stock = stock_response.get('stock_product', 0)
                    if current_stock is None:
                        availability_check.append({
                            'product_id': item.product_public_id,
                            'available': False,
                            'current_stock': current_stock,
                            'required': item.quantiy 
                        })
                    elif current_stock < item.quantity:
                        availability_check.append({
                            'product_id': item.product_public_id,
                            'available': False,
                            'current_stock': current_stock,
                            'required': item.quantity
                        })
                    else:
                        availability_check.append({
                            'product_id': item.product_public_id,
                            'available': True,
                            'current_stock': current_stock
                        })
                except Exception as e:
                    logger.error(f'Error verificando el stock de {item.product_public_id}')      
                    availability_check.append({
                        'product_id': item.product_public_id,
                        'available': False,
                        'error': str(e)
                    })  
            
            all_available = all(item['available'] for item in availability_check)
            
            return {
                'all_available': all_available,
                'details': availability_check
            }

        except OrderNotFoundException:
            raise    
        except Exception as e:
            logger.error(f"Error verificando disponibilidad: {str(e)}")
            return {
                'all_available': False,
                'error': str(e)
            }
            
    
    @staticmethod
    def list_orders_no_delivered() -> Optional[List[Order]]:
        return OrderDAO.get_all_no_delivered()

    @staticmethod
    def list_orders_with_filters(filtros):
        return OrderDAO.find_by_filter(**filtros) # Unpack filtros' dictionary elements to pass them to args of the function

    @staticmethod
    def list_orders(size: int, page: int):
        return OrderDAO.get_all(size, page)
    
    @staticmethod
    def update_product_stock(order_id: str) -> dict:

        """
        Solicita al microservicio de contenido que actualice el stock del producto
        """

        try:
            order = OrderDAO.find_by_public_id(order_id)

            if not order:
                raise ProductNotFoundException(order_id, f"Error al encontrar el producto {order_id}")
            
            results = [] # Almacenará los resultados que arroja el microservicio de contenido
            successful_updates = [] # Almacenará todos los resultados exitosos que arroka el microservicio de contenido
            for item in order.items:
                try: 
                    stock_result = content_client.update_product_stock_by_id(
                        item.product_public_id,
                        -item.quantity)
                    
                    if stock_result is None:
                        results.append({
                            'product_id': item.product_public_id,
                            'success': False,
                            'error': 'Servicio de contenido no disponible'
                        })

                    success = stock_result.get('success', False)

                    results.append({
                        'product_id': item.product_public_id,
                        'success': success,
                        'error': stock_result.get('error') if not success else None
                    })

                    if success: 
                        successful_updates.append({
                            'product_id': item.product_public_id,
                            'quantity_changed': item.quantity
                        })
                    else:
                        OrderService._rollback_stock_updates(content_client, successful_updates) # Desacemos los que se hayan actualizado
                        break # No nos interesa seguir actualizando si uno ya ha fallado    
                except Exception as e:
                    logger.error(f"Error actualizando stock de {item.product_public_id}: {e}")
                    results.append({
                        'product_id': item.product_public_id,
                        'success': False,
                        'error': str(e)
                    })
                    # Rollback
                    OrderService._rollback_stock_updates(
                        content_client, 
                        successful_updates
                    )
                    break

            all_success = all(result['success'] for result in results)    

            if all_success:
                return {
                    'success': True,
                    'message': 'Stock de todos los productos de la compra actualizados correctamente',
                    'details': results
                }
            else:
                return {
                    'success': False,
                    'message': 'Fallo en la actualización del stock sobre alguno o todos los productos de la compra',
                    'details': results
                }
            
        except OrderNotFoundException:
            raise    
        except Exception as e:
            logger.error(f"Error actualizando stock: {str(e)}")
            raise ProductNotFoundException(f"Error actualizando stock: {str(e)}")
        
    @staticmethod
    def _rollback_stock_updates(content_client, updates: List[dict]):
        """Revierte actualizaciones de stock en caso de fallo"""
        logger.warning(f"Iniciando rollback de {len(updates)} actualizaciones de stock")
        
        for update in updates:
            try:
                content_client.update_product_stock_by_id(
                    update['product_id'],
                    update['quantity_changed']  # Restaurar cantidad
                )
                logger.info(f"Rollback exitoso para {update['product_id']}")
            except Exception as e:
                logger.error(f"Error en rollback de {update['product_id']}: {e}")    

    @staticmethod
    def save(order: CreateOrderRequestDTO, username: str):
        """
            Convert CreateOrderRequestDTO into OrderItem SQLAlchemy
        """
        try:
            user_info = user_client.get_seller_by_username(username)
        
            if not user_info:
                raise ValueError(f"Error, usuario {username} no encontrado") 

            logger.info(f"Usuario {username} encontrado")
            
            total_price = 0.0
            order_items = []

            for item_dto in order.items:
                # Obtain order's products info
                #product_info = OrderService.find_order_item(item_dto.productId)
                product_info = content_client.get_product_by_id(item_dto.productId)

                if not product_info or 'price' not in product_info:
                    raise ProductNotFoundException(
                        "productId",
                        f"Product {item_dto.productId} no encontrado o sin precio incluido"
                    )
                
                # Obtain seller info
                artist_info = product_info.get('artist', {})
                
                item_price = item_dto.quantity * product_info['price']
                total_price += item_price
                
                new_order_item = OrderItem(
                    product_public_id = item_dto.productId,
                    product_name = product_info.get('product_name', 'Sin nombre'),
                    product_image_src = product_info.get('product_image_src', ''),
                    product_description = product_info.get('product_description', ''),
                    #seller_username=product_info.seller_username,
                    seller_username = artist_info.get('username', ''),
                    #seller_name=product_info.seller_name,
                    seller_name = artist_info.get('artisticName', ''),
                    #seller_pfp=product_info.seller_pfp,
                    seller_pfp = artist_info.get('pfp', ''),
                    quantity=item_dto.quantity,
                    price=product_info['price'],
                    total=total_price
                )

                order_items.append(new_order_item)

            new_order = Order(
                public_id = OrderService.generate_public_id(),
                made_by_username = username,
                status = OrderStatus.PENDING,
                total = total_price,
                created_at = datetime.now(UTC),
                items = order_items
            )    
            # Save info in database
            saved_info = OrderDAO.add_order(new_order, username)
            logger.info(f"Order {saved_info} creado correctamente")

            return saved_info
        
        except ProductNotFoundException as e:
            raise e
        except Exception as e:
            print(f"Error en OrderService.create_order_from_dto: {str(e)}")
            raise e    
        
    @staticmethod
    def process_order_payment(order_id: str, order_data: dict) -> dict:
        """
        Procesa el pago de una compra utilizando el cliente de pagos
        """
        try:
            # Obtenemos la info de la compra
            order = OrderService.find_order_by_public_id(order_id)
            if not order:
                raise OrderNotFoundException("order_id", f"Compra con id {order_id} no encontrada")
            
            payment_result = payment_client.procesamiento_pagos(order_data)

            if payment_result is None:
                raise PaymentProcessingException("Servicio de pagos no disponible")

            if payment_result['success'] and payment_result['status'] == 'COMPLETED':
                order_info = OrderDAO.mark_order_as_paid(order_id)
                
                return {
                    'success': True,
                    'payment_id': payment_result['payment_id'],
                    'status': payment_result['status'],
                    'message': 'Pago realizado exitosamente',
                    'transaction_data': order_info
                }
            else:
                return {
                    'success': False,
                    'error': payment_result.get('error'),
                    'message': 'Error en el procesamiento de pagos'
                }

        except (OrderNotFoundException, PaymentProcessingException):
            raise    
        except Exception as e:
            logger.error(f"Error procesando pago de orden: {str(e)}")
            raise ProductNotFoundException(f"Error procesando pago: {str(e)}")    
    
    @staticmethod
    def find_order_by_seller(username: str, page: int, size: int):
        return OrderDAO.get_orders_by_seller(username, page, size)