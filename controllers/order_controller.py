from flask import Blueprint, request, jsonify, Response
from service import order_service
from dto.order_dto import OrderResponseDTO, OrderPageDTO, CreateOrderRequestDTO
from decorator.tokenDecorator import token_required
from decorator.logRequestDecorator import log
import logging

logger = logging.getLogger(__name__)

order_bp = Blueprint('order_bp', __name__)

@order_bp.route('/orders', methods=['GET'])
#@token_required    -> Validate user token
@log('../logs/ficherosalida.log')
def procesar_compras():
    filters = {}
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
                return jsonify({'error 7': 'Page must be greater or equal to 0'}), 400
            
            if filters['size'] <= 0 or filters['size'] > 100:
                return jsonify({'error 8': 'The size of the page must be between 1 and 100'}), 400

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
        return jsonify({'error': str(e)}), 500