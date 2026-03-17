from django.test import TestCase, Client
from checkout_api.models import Order
# from checkout_api.serializers import ProductSerializer, CartSerializer, CartItemSerializer
from decimal import *
from django.urls import reverse
from unittest.mock import patch
from django.http import QueryDict
from django.test import TransactionTestCase
import redis
from django.conf import settings

# rd_instance = redis.Redis(host='redis://127.0.0.1', port=6379, decode_responses=True)
rd_instance = redis.Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)

class PlaceOrderTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post(self):
        url = f'/api/checkout/place-order/'

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], "Order drafted! Now complete the payment to confirm it.")    

class StripeWebhookTestCase(TestCase):
    def test_post(self):
        url = f'/api/checkout/webhook/'

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], "Order confirmed! Wait at the front door for 4 months.")  
