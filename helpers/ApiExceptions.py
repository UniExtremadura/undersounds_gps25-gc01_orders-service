from datetime import datetime

class APIException(Exception):
    """Excepción base para errores de la API"""
    def __init__(self, message, status=400, error=None):
        super().__init__()
        self.message = message
        self.status = status
        self.error = error if error else 'Error'