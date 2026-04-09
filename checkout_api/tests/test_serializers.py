from django.test import TestCase
from checkout_api.models import Order
from checkout_api.serializers import CartItemSerializer, OrderDataSerializer, OrderSerializer, OrderItemSerializer
from decimal import *
from django.urls import reverse
from django.test.client import RequestFactory

class OrderDataSerializerTestCase(TestCase):
    def test_instance_validation(self):
        data = {}

        serializer = OrderDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(errors), 1)
        self.assertEqual(str(errors['contact_email'][0]), 'This field is required.')

        data['contact_email'] = ''

        serializer = OrderDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['contact_email'][0]), 'This field may not be blank.')

        data['contact_email'] = 'emailaddress'
        serializer = OrderDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['contact_email'][0]), 'Enter a valid email address.')

        data['contact_email'] = 'johndoe@example.com'
        
        serializer = OrderDataSerializer(data=data)
        self.assertTrue(serializer.is_valid())

class OrderSerializerTestCase(TestCase):
    def test_instance_validation(self):
        data = {}

        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(errors), 3)
        self.assertEqual(str(errors['contact_email'][0]), 'This field is required.')
        self.assertEqual(str(errors['total'][0]), 'This field is required.')
        self.assertEqual(str(errors['payment_intent_id'][0]), 'This field is required.')

        data['contact_email'] = 'emailaddress'
        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['contact_email'][0]), 'Enter a valid email address.')

        data['contact_email'] = 'johndoe@example.com'
        data['total'] = 1200
        data['payment_intent_id'] = '123'
        
        serializer = OrderDataSerializer(data=data)
        self.assertTrue(serializer.is_valid())

class OrderItemSerializerTestCase(TestCase):
    def setUp(self):
        self.order = Order.objects.create(status=Order.PAID,
            total=4599,
            contact_email='johndoe@example.com',
            payment_intent_id='123')

    def test_instance_validation(self):
        data = {}

        serializer = OrderItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(errors), 3)
        self.assertEqual(str(errors['item_id'][0]), 'This field is required.')
        self.assertEqual(str(errors['quantity'][0]), 'This field is required.')
        self.assertEqual(str(errors['order'][0]), 'This field is required.')

        data['order'] = '123'
        serializer = OrderItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['order'][0]), f'Invalid pk "{data['order']}" - object does not exist.')

        data['order'] = self.order.pk
        data['item_id'] = 123
        data['quantity'] = 60

        serializer = OrderItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['item_id'][0]), f"Product with id {data['item_id']} doesn't exist.")

        data['order'] = self.order.pk
        data['item_id'] = 2
        data['quantity'] = 60
        serializer = OrderItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['quantity'][0]), 'Quantity exceeds the product.')

        data['order'] = self.order.pk
        data['item_id'] = 2
        data['quantity'] = 6
        
        serializer = OrderItemSerializer(data=data)
        self.assertTrue(serializer.is_valid())

class CartItemSerializerTestCase(TestCase):
    def test_instance_validation(self):
        data = {}

        serializer = CartItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(errors), 2)
        self.assertEqual(str(errors['product_id'][0]), 'This field is required.')
        self.assertEqual(str(errors['product_quantity'][0]), 'This field is required.')

        data['product_id'] = 123
        data['product_quantity'] = 6

        serializer = CartItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(errors), 1)
        self.assertEqual(str(errors['product_id'][0]), f"Product with id {data['product_id']} doesn't exist.")

        data['product_id'] = 1
        data['product_quantity'] = 6

        serializer = CartItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(errors), 1)
        self.assertEqual(str(errors['product_quantity'][0]), 'Quantity exceeds the product.')

        data['product_id'] = 1
        data['product_quantity'] = 5

        serializer = CartItemSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        

