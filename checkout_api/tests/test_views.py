from django.test import TestCase
from rest_framework.test import APIClient
from checkout_api.models import Order
from checkout_api.views import demo_products
from decimal import *
from django.urls import reverse
from unittest.mock import patch
from django.http import QueryDict
from django.test import TransactionTestCase
import redis
from django.conf import settings

# rd_instance = redis.Redis(host='redis://127.0.0.1', port=6379, decode_responses=True)
rd_instance = redis.Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)

class ProductListView(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get(self):
        url = f'/api/checkout/demo-products/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), len(demo_products))    

        for index, item in enumerate(response.json()):
            self.assertEqual(item, demo_products[index])    

class PlaceOrderTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_post(self):
        url = f'/api/checkout/place-order/'

        data = {}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()['msg'], 'Key "order" is required')

        data = {'order': 123}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.json()), 1)
        cart_items_msg = 'Key "cart_items" is required and it must be a list'
        self.assertEqual(response.json()['msg'], cart_items_msg)

        data = {'order': 123, 'cart_items': 123}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.json()['msg'], cart_items_msg)

        data = {'order': 123, 'cart_items': []}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.json()['msg'], cart_items_msg)

        data = {'order': 123, 'cart_items': [{}, {}]}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.json()['msg_item_1']), 2)

        data = {'order': 123, 'cart_items': [{'product_id': 1, 'product_quantity': 4}, {'product_id': 2, 'product_quantity': 6}]}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.json()['msg']), 1)

        data = {'order': {'contact_email': 'test@test.com'}, 'cart_items': [{'product_id': 1, 'product_quantity': 4}, {'product_id': 2, 'product_quantity': 6}]}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], "Order drafted! Now complete the payment to confirm it.")

class StripeWebhookTestCase(TestCase):
    def test_post(self):
        url = f'/api/checkout/webhook/'

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], "Order confirmed! Wait at the front door for 4 months.")  
