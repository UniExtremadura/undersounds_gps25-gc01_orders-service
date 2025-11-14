from flask import Blueprint, request, jsonify, Response, g
from service import order_service
from dto.order_dto import OrderResponseDTO, OrderPageDTO, CreateOrderRequestDTO
from decorator.tokenDecorator import token_required
from decorator.roleDecorator import role_validator
from decorator.logRequestDecorator import log
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

order_bp = Blueprint('order_bp', __name__)

@order_bp.route('/orders/<string:orderId>', methods=['GET'])
#@token_required -> Validate user token
@log('../logs/ficherosalida.log')
def proccess_orders_by_id(orderId: str):
    """Responde al cliente con la información de las compras relacionadas con el id solicitado"""
    try:
        # Llamo al servicio para buscar compras que coincidan con orderId
        order = order_service.OrderService.find_order(orderId)

        if order:
            order_dict = order_service.OrderService.order_to_dict(order)
            # Validate the entry Order with Pydantic. Converting SQLAlchemy obj -> Pydantic DTO
            orderDTO = OrderResponseDTO.model_validate(order_dict)
            return Response(
                orderDTO.model_dump_json(),
                status=200,
                mimetype='application/json'
            )
        else:
            return Response(
                response = f"La compra {orderId} no existe",
                status = 404,
                mimetype = 'application/json'
            )

    except ValueError as e:
        logger.warning(f"Error de validación: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Error interno: {str(e)}")
        return jsonify({'message': str(e)}), 500
    
@order_bp.route('/orders/<string:orderId>', methods=['PATCH'])
#@token_required -> Validate user token
#@role_validator('admin') -> Validate if the user requester is registered as an admin to do this operation
@log('../logs/ficherosalida.log')
def update_order_by_id(orderId: str):
    try:
        data = request.get_json() # Obtenemos los datos del cuerpo de la consulta
                
        if not data:
            return jsonify({'error': 'Datos de actualización requeridos'}), 400
        
        is_updatable = order_service.OrderService.is_order_updatable(orderId)

        if not is_updatable:
            return jsonify({
                f"La orden {orderId} no existe o no se puede actualizar (ya fue enviada, cancelada o entregada)"
            }), 400
        
        order_update = order_service.OrderService.update_order(orderId, data)

        if order_update:

            order_updated_dict = order_service.OrderService.order_to_dict(order_update)
            orderDTO_updated = OrderResponseDTO.model_validate(order_updated_dict)

            return Response(
                response = orderDTO_updated.model_dump_json(),
                status = 200,
                mimetype = 'application/json'
            )
        
        else:
            return Response(
                response = f"La compra {orderId} no existe",
                status = 404,
                mimetype = 'application/json'
            )
        
    except ValueError as e:
        logger.warning(f"Error de validación: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error interno: {str(e)}")
        return jsonify({'error': str(e)}), 500    

@order_bp.route('/orders', methods=['GET'])
@token_required    #-> Validate user token
@log('../logs/ficherosalida.log')
def procesar_compras():
    """Responde al cliente con información completa de todas las compras realizadas o por filtros"""
    filters = {}
    orders_tuple = None
    try:
        if request.method == 'GET': # Save the query params of the HTTP request in a dictionary
            filters['seller'] = request.args.get('seller')
            filters['status'] = request.args.get('status')
            filters['dateFrom'] = request.args.get('dateFrom')
            filters['dateTo'] = request.args.get('dateTo')
            filters['page'] = request.args.get('page', 0, type=int)
            filters['size'] = request.args.get('size', 20, type=int)

            # Paginating validation
            if filters['page'] < 0:
                return jsonify({'code': 400, 'message': 'La pagina debe de ser mayor o igual a 0'}), 400
            
            if filters['size'] < 20 or filters['size'] > 100:
                return jsonify({'code': 400, 'message': 'El tamaño de la página debe de ser mayor o igual a 20'}), 400

            # CASE: No filter applied
            if filters is None: 
                orders_tuple = order_service.OrderService.list_orders(filters['size'], filters['page'])
            else:
                orders_tuple = order_service.OrderService.list_orders_with_filters(filters)    

            # Access to the Tuple elements of orders
            order_list = orders_tuple[0]
            total_elements = orders_tuple[1]
            total_pages = orders_tuple[2]

            # Convert orders into Page DTO
            pageDTO = OrderPageDTO(
                content = [OrderResponseDTO.from_orm(order) for order in order_list],
                totalElements = total_elements,
                totalPages = total_pages,
                page = filters['page'],
                size = filters['size']
            )    

            return Response(
                pageDTO.model_dump_json(),
                status=200,
                mimetype='application/json'
            )
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@order_bp.route('/orders', methods=['POST'])
#@token_required -> Validate user token
#@role_validator('admin') -> Validate if the user requester is registered as an admin to do this operation
@log('../logs/ficherosalida.log')
def create_order():
    """Responde al usuario con la información de compra que acaba de crear"""
    try:
        # Obtain data from the request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos json no requeridos'}), 400
        
        # Validate data request with Pylantic
        # Data must have items and not duplicates - products | This DTO validates it
        data_validated = CreateOrderRequestDTO.model_validate(data)

        # Get user from JWT, now is hardcoded
        current_user = "usuario_actual"

        order_created = order_service.OrderService.save(
            data_validated, 
            current_user
        )
        
        # Converto to DTO the response
        order_created_dto = OrderResponseDTO.from_orm(order_created)

        return Response(
            order_created_dto.model_dump_json(),
            status=201,
            mimetype='application/json'
        )
        
    except order_service.ProductNotFoundException as e:
        return jsonify({
            'error': 'Producto no encontrado',
            'details': str(e)
        }), 404
        
    except ValueError as e:
        return jsonify({
            'error': 'Error de validación',
            'details': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500
    
@order_bp.route('/orders/<string:orderId>', methods=['DELETE'])
#@token_required -> Validate user token
@log('../logs/ficherosalida.log')   
def delete_order_by_id(orderId: str):
    try: 
        deleted = order_service.OrderService.delete(orderId)

        if deleted:
            # Response verifying to user that the order was successfuly deleted
            return Response(
                response="Compra eliminada correctamente",
                status=204,
                mimetype='application/json'
            )
        else:
            return Response(
                response = f"La compra {orderId} no existe",
                status = 404,
                mimetype = 'application/json'
            )
        
    except ValueError as e:
        logger.warning(f"Error de validación: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error interno: {str(e)}")
        return jsonify({'error': str(e)}), 500    

@order_bp.route('/orders/<string:orderId>/confirm', methods=['POST'])
#@token_required
@log('../logs/ficherosalida.log')
def confirm_order(orderId: str):
    """
    Confirma una compra: verifica stock → procesa pago → actualiza stock
    """
    try:
        # 1. Verificar que la orden existe
        order = order_service.OrderService.find_order(orderId)
        if not order:
            return jsonify({'error': f'La orden {orderId} no existe'}), 404
        
        # 2. Validar que la orden esté en estado procesable
        if not order_service.OrderService.is_order_confirm(orderId):
            return jsonify({
                'error': f'La orden {orderId} no puede ser confirmada'
            }), 400
        
        # 3. Verificar disponibilidad de stock ANTES del pago
        stock_availability = order_service.OrderService.check_stock_availability(orderId)
        if not stock_availability['all_available']:
            return jsonify({
                'error': 'Stock insuficiente para algunos productos',
                'details': stock_availability.get('details')
            }), 409  # Conflict
        
        # 4. Obtener datos de pago del request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos de pago requeridos'}), 400
        
        # 5. Procesar pago
        payment_result = order_service.OrderService.process_order_payment(orderId, data)

        # Obtenemos la información del pedido actualizada
        order_info = payment_result['transaction_data']
        
        if not payment_result['success']:
            return jsonify({
                'error': 'Error en el procesamiento del pago',
                'details': payment_result.get('error', 'Error desconocido')
            }), 402
        
        # 6. Actualizar stock (solo si el pago fue exitoso)
        stock_update_result = order_service.OrderService.update_product_stock(orderId)
        
        """if not stock_update_result['success']:
            # Revertir el pago si la actualización de stock falla
            order_service.OrderService.reverse_payment(orderId)
            return jsonify({
                'error': 'Error al actualizar el stock',
                'details': stock_update_result.get('details', 'Error desconocido')
            }), 500"""
        
        order_dict = order_service.OrderService.order_to_dict(order_info)
        orderDTO = OrderResponseDTO.model_validate(order_dict)
        
        return Response(
            orderDTO.model_dump_json(),
            status=200,
            mimetype='application/json'
        )
        
    except order_service.OrderNotFoundException as e:
        return jsonify({'error': str(e)}), 404
    except order_service.PaymentProcessingException as e:
        return jsonify({'error': 'Error en el procesamiento del pago', 'details': str(e)}), 502
    except Exception as e:
        logger.error(f"Error interno: {str(e)}")
        return jsonify({'error': str(e)}), 500      