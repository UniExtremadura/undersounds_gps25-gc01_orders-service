import requests
from typing import Optional
from circuitbreaker import circuit
from config import CircuitBreakerPersonalizado, eureka_client
from clients.base_client import BaseClient
import logging

logger = logging.getLogger(__name__)

class PaymentClient(BaseClient):
    def __init__(self, app):
        super().__init__(app, "payment-service")
        #self.service_name = "payment-service"  # Nombre que tiene registrado Eureka para el microservicio de usuarios
        self.base_url = app.config.get('PAYMENT_SERVICE_URL')
        self.timeout = 5
    
    def _get_payment_service_url(self) -> str:
        try:
            return eureka_client.get_app_url(self.service_name)
        except Exception as e:
            logger.error(f"Error obteniendo la URL para {self.service_name}: {e}")
            return ""


    @circuit(cls=CircuitBreakerPersonalizado)
    def procesamiento_pagos(self, order_data: dict) -> Optional[dict]:
        """
        Procesamiento de un pago a través del microservicio de pagos
        Utiliza el método POST /api/payments
        """
        try:
            
            url = f"{self.base_url}/api/payments"
            
            response = self._make_request('POST', url, json = order_data)
            #baseUrl = self._get_user_service_url() -> Eureka
            logger.info(f"Enviado pago al microservicio: {url}")

            if response.status_code == 200:
                payment_response = response.json()
                logger.info(f"Pago procesado exitosamente: {payment_response.get('id')}")
                return {
                    'success': True,
                    'payment_id': payment_response.get('id'),
                    'status': payment_response.get('status'),
                    'transaction_data': payment_response
                }

            else:
                    logger.error(f"Error en pago: {response.status_code} - {response.text}")
                    return {
                        'success': False,
                        'error': response.json().get('error', 'Error desconocido en el servicio de pagos'),
                        'status_code': response.status_code
                    }
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexión con el servicio de pagos: {str(e)}")
            return {
                'success': False,
                'error': 'No se pudo conectar con el servicio de pagos'
            }
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout en servicio de pagos: {str(e)}")
            return {
                'success': False,
                'error': 'Timeout en el servicio de pagos'
            }
        except Exception as e:
            logger.error(f"Error inesperado en pago: {str(e)}")
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }
        
    @circuit(cls=CircuitBreakerPersonalizado)
    def update_payment_status(self, purchase_id: str, status: str) -> Optional[dict]:
        """
        Actualizar el estado de un pago
        Utiliza el endpoint PATCH /api/payments/{purchase_id}
        """    

        try:
            url = f"{self.base_url}/api/payments/{purchase_id}"

            payment_payload = {
                'status': 'COMPLETED'
            }

            response = self._make_request('PATCH', url, json = payment_payload)

            if response.status_code == 200:
                logger.info(f"Modificado correctamente el estado de pago en el que se encuentra {purchase_id}")
                payment_response = response.json()
                return {
                    'success': True,
                    'payment_id': payment_response.get('id'),
                    'status': payment_response.get('status'),
                    'transaction_data': payment_response
                }
            else:
                logger.error(f"Error consultando el pago: {purchase_id}")
                return {
                    'success': False,
                    'error': response.json().get('error', 'Error desconocido en el servicio de pagos'),
                    'status_code': response.status_code
                }
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexión con el servicio de pagos: {str(e)}")
            return {
                'success': False,
                'error': 'No se pudo conectar con el servicio de pagos'
            }
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout en servicio de pagos: {str(e)}")
            return {
                'success': False,
                'error': 'Timeout en el servicio de pagos'
            }
        except Exception as e:
            logger.error(f"Error inesperado en pago: {str(e)}")
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }
        
    @circuit(cls=CircuitBreakerPersonalizado)    
    def get_payment_satus(self, purchase_id : str) -> Optional[dict]:
        """
        Comprobación del estado de un pago
        Utiliza el endpoint GET /api/payments con query parameter purchase_id
        """    

        try:
            url = f"{self.base_url}/api/payments"

            params = {
                'purchaseId' : purchase_id
            }

            response = self._make_request('GET', url, params = params)

            if response.status_code == 200:
                logger.info(f"Respuesta satisfactoria con parámetro: {purchase_id}")
                payment_response = response.json()
                return {
                    'success': True,
                    'payment_id': payment_response.get('id'),
                    'status': payment_response.get('status'),
                    'transaction_data' : payment_response
                }
            else:
                logger.error(f"Error consultando el pago: {purchase_id}")
                return {
                    'success': False,
                    'error': response.json().get('error', 'Error desconocido en el servicio de pagos'),
                    'status_code': response.status_code
                }
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexión con el servicio de pagos: {str(e)}")
            return {
                'success': False,
                'error': 'No se pudo conectar con el servicio de pagos'
            }
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout en servicio de pagos: {str(e)}")
            return {
                'success': False,
                'error': 'Timeout en el servicio de pagos'
            }
        except Exception as e:
            logger.error(f"Error inesperado en pago: {str(e)}")
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }
        