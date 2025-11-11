from clients.content_client import ContentClient
from clients.user_client import UserClient
from clients.payment_client import PaymentClient
from config import Config

user_client = None
content_client = None
payment_client = None

def init_client(app):
    global user_client, content_client, payment_client
    user_client = UserClient(app)
    content_client = ContentClient(app)
    payment_client = PaymentClient(app)