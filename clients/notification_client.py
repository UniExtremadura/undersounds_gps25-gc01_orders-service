import requests
from typing import Optional
from flask import current_app
from circuitbreaker import circuit
from config import CircuitBreakerPersonalizado
from clients.base_client import BaseClient
import logging

logger = logging.getLogger(__name__)

class NotificationClient(BaseClient):

    def __init__(self, app):
        super().__init__(app, "notification-service")
        self.base_url = app.config.get('NOTIFICATION_SERVICE_URL')
        self.timeout = 5