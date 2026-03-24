from django.test import TestCase
from checkout_api.serializers import CartItemSerializer, OrderDataSerializer
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
        

