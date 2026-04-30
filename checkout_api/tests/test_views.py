from django.test import TestCase
from rest_framework.test import APIClient
from checkout_api.models import Order, OrderItem
from checkout_api.views import demo_products
from decimal import *
from django.urls import reverse
from unittest.mock import patch
from django.http import QueryDict
from django.test import TransactionTestCase
import redis
from django.conf import settings
import stripe
from types import SimpleNamespace

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

    @patch('checkout_api.views.stripe.PaymentIntent.create')
    def test_post(self, mock_stripe):
        mock_stripe.return_value = {
            'client_secret': '123',
            'id': '321',
            'payment_method': 'card'
        }


        url = f'/api/checkout/place-order/'

        data = {}

        # Test "validate input"
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()['order'], ['This field is required.'])
        self.assertEqual(response.json()['cart_items'], ['This field is required.'])

        # Test success
        data = {'order': {'contact_email': 'test@test.com'}, 'cart_items': [{'product_id': 1, 'product_quantity': 4}, {'product_id': 2, 'product_quantity': 6}]}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], 'Order drafted! Now complete the payment to confirm it.')
        
        self.assertEqual(response.json()['totals'], 41200)

        mock_stripe.assert_called_once()

        mock_stripe.assert_called_with(amount= int(response.json()['totals']),
            currency= 'usd', automatic_payment_methods={'enabled': True})
        
        saved_order = Order.objects.all().first()

        self.assertTrue(saved_order)
        self.assertEqual(saved_order.total, 41200)
        self.assertEqual(saved_order.contact_email, data['order']['contact_email'])
        self.assertEqual(saved_order.status, Order.PENDING)

        order_items = OrderItem.objects.all()

        self.assertEqual(len(order_items), 2)
        self.assertEqual(order_items[0].item_id, data['cart_items'][1]['product_id'])
        self.assertEqual(order_items[1].item_id, data['cart_items'][0]['product_id'])

class StripeWebhookTestCase(TestCase):
    def setUp(self):
        self.order = Order.objects.create(contact_email='test@test.com', total=2500, payment_intent_id='123')
        OrderItem.objects.create(item_id='1', title='Abstract Horizon Painting', price=5500, quantity=4, order=self.order)
        OrderItem.objects.create(item_id='2', title='Minimalist Ceramic Vase', price=3200, quantity=10, order=self.order)
        OrderItem.objects.create(item_id='3', title='Handwoven Cotton Throw',price=4500, quantity=2, order=self.order)
    @patch('checkout_api.views.sendreciept_task')
    @patch('checkout_api.views.stripe.Event.construct_from')
    def test_post_successful(self, mock_event, mock_task):
        url = f'/api/checkout/webhook/'

        # mocking payment
        data = SimpleNamespace(object={'id': self.order.payment_intent_id})
        event_obj = SimpleNamespace(type='payment_intent.succeeded', data=data)

        mock_event.return_value = event_obj

        data = {
            'test': 123
        }

        # Test payment_intent.payment_failed
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], 'Order paid successfully!')  

        modified_order = Order.objects.get(pk=self.order.pk)

        self.assertEqual(modified_order.status, Order.PAID)

        mock_task.delay.assert_called_once_with(modified_order.pk)

    @patch('checkout_api.views.sendreciept_task')
    @patch('checkout_api.views.stripe.Event.construct_from')
    def test_post_failures(self, mock_event, mock_task):
        url = f'/api/checkout/webhook/'

        # mocking payment
        data = SimpleNamespace(object={'id': self.order.payment_intent_id})
        event_obj = SimpleNamespace(type='payment_intent.payment_failed', data=data)

        mock_event.return_value = event_obj

        data = {
            'test': 123
        }

        # Test payment_intent.payment_failed
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['msg'], 'Order failed and cancelled!')  


        modified_order = Order.objects.get(pk=self.order.pk)
        
        mock_task.delay.assert_called_once_with(modified_order.pk)

        self.assertEqual(modified_order.status, Order.CANCELLED)

        event_obj = SimpleNamespace(type='payment_intent.payment_something', data=data)

        mock_event.return_value = event_obj
        
        # Test payment_intent.payment_something
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['msg'], f'Unhandled event type {event_obj.type}')

        mock_event.side_effect = ValueError("error, bro")

        # Test 'validate payment made'
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['msg'], 'Error loading the payment event!')

