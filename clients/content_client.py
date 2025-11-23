import requests
from typing import Optional
from flask import current_app
from circuitbreaker import circuit
from config import CircuitBreakerPersonalizado
from clients.base_client import BaseClient
import logging

logger = logging.getLogger(__name__)

class ContentClient(BaseClient):

    def __init__(self, app):
        super().__init__(app, "content-service")
        self.base_url = app.config.get('CONTENT_SERVICE_URL')
        self.timeout = 5

    @circuit(cls=CircuitBreakerPersonalizado)
    def get_product_by_id(self, publicId: str) -> Optional[dict]:
        """Obtains product info"""
        try:

            url = f"{self.base_url}/products/public/{publicId}"
            
            response = self._make_request('GET', url)
            
            # Control if content's microservice is down or in panic
            if response.status_code == 404:
                return None # Non existing user
            if response.status_code >= 500: # Microservice internal server error
                logger.error(f"Error al intentar comunicarte con el microservicio de contenido {response.status_code}")
                return None

            response.raise_for_status()
            
            # Response comes as a JSON format
            data = response.json()
            if data.get('success'):
                return data.get('data') # Contains the product's info
            return None
    
        except requests.exceptions.ConnectionError as e:
            raise Exception("Servicio de contenido no disponible")
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error al intentar obtener el pedido {publicId}")
            return None
        
    @circuit(cls=CircuitBreakerPersonalizado)
    def  get_product_stock_by_id(self, product_id: str) -> Optional[dict]:
        try:
            url = f"{self.base_url}/products/public/{product_id}"
            print(self.app.config.get('CONTENT_SERVICE_URL'))
            print(url)

            response = self._make_request('GET', url)

            data = response.json()
            print(data, flush=True)

            if data.get('success') is True:
                return {
                    'success': True,
                    'stock_product': data.get('data').get('stock'),
                    'message': f'Recuperación de stock para el producto {product_id} exitosa'
                }
            else:
                return {
                    'success': False,
                    'message': f'Recuperación de stock para el producto {product_id} fallida'
                }   
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexión con el servicio de contenido: {str(e)}")
            return {
                'success': False,
                'error': 'No se pudo conectar con el servicio de contenido'
            }
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout en servicio de contenido: {str(e)}")
            return {
                'success': False,
                'error': 'Timeout en el servicio de contenido'
            }
        except Exception as e:
            logger.error(f"Error inesperado en contenido: {str(e)}")
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }       
        
    @circuit(cls=CircuitBreakerPersonalizado)
    def update_product_stock_by_id(self, productId: str, newStock: int) -> Optional[dict]:
        try:
            url = f"{self.base_url}/products/{productId}/stock"

            params = {
                'newStock': newStock
            }

            response = self._make_request('PATCH', url, params = params)   

            if response.status_code == 200:
                product_info = response.json()
                return {
                    'success': True,
                    'message': 'Stock actualizado correctamente',
                    'transaction_data': product_info
                } 
            else:
                logger.error(f"Error actualizando stock: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': response.json().get('error', 'Error actualizando stock'),
                    'status_code': response.status_code
                }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error de conexión con servicio de contenido: {str(e)}")
            return {
                'success': False,
                'error': 'No se pudo conectar con el servicio de contenido'
            }
        except Exception as e:
            logger.error(f"Error inesperado actualizando stock: {str(e)}")
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }    

    @circuit(cls=CircuitBreakerPersonalizado)    
    def get_songs_by_id(self, songId: str) -> Optional[dict]:
        try:
            url = f"{self.base_url}/products/public/{songId}"
            response = self._make_request('GET', url)  

            # Control if content's microservice is down or in panic
            if response.status_code == 404:
                return None # Non existing product
            if response.status_code >= 500: # Microservice internal server error
                current_app.logger.error(f"Error al intentar comunicarte con el microservicio de contenido {response.status_code}")
                return None

            response.raise_for_status()

            data = response.json()
            if data.get('success'):
                return data.get('data')
            return None
        
        except requests.exceptions.ConnectionError as e:
            raise Exception("Servicio de contenido no disponible")
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error al intentar obtener la cancion {songId}")
            return None

    @circuit(cls=CircuitBreakerPersonalizado)
    def get_albums_by_id(self, albumId: str) -> Optional[dict]:
        try:
            url = f"{self.base_url}/products/public/{albumId}"
            response = self._make_request('GET', url)  

            # Control if content's microservice is down or in panic
            if response.status_code == 404:
                return None # Non existing product
            if response.status_code >= 500: # Microservice internal server error
                current_app.logger.error(f"Error al intentar comunicarte con el microservicio de contenido {response.status_code}")
                return None

            response.raise_for_status()

            data = response.json()
            if data.get('success'):
                return data.get('data')
            return None
        
        except requests.exceptions.ConnectionError as e:
            raise Exception("Servicio de contenido no disponible")
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error al intentar obtener el album {albumId}")
            return None
