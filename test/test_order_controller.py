# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.test import BaseTestCase


class TestOrderController(BaseTestCase):
    """OrderController integration test stubs"""

    def test_orders_get(self):
        """Test case for orders_get

        Listar compras con filtros
        """
        query_string = [('seller', None),
                        ('status', None),
                        ('dateFrom', None),
                        ('dateTo', None),
                        ('page', None),
                        ('size', None)]
        response = self.client.open(
            '/orders',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_orders_order_id_delete(self):
        """Test case for orders_order_id_delete

        Eliminar una compra
        """
        response = self.client.open(
            '/orders/{orderId}'.format(orderId=None),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_orders_order_id_get(self):
        """Test case for orders_order_id_get

        Obtener una compra
        """
        response = self.client.open(
            '/orders/{orderId}'.format(orderId=None),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_orders_order_id_patch(self):
        """Test case for orders_order_id_patch

        Actualizar algún atributo de una compra
        """
        response = self.client.open(
            '/orders/{orderId}'.format(orderId=None),
            method='PATCH')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_orders_post(self):
        """Test case for orders_post

        Crear una nueva compra
        """
        response = self.client.open(
            '/orders',
            method='POST')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
