from django.test import TestCase
from checkout_api.serializers import CartItemSerializer, OrderSerializer, OrderItemSerializer, OrderDataSerializer
from decimal import *
from django.urls import reverse
from django.test.client import RequestFactory

class OrderDataSerializerTestCase(TestCase):
    def test_instance_validation(self):
        data = {}

        serializer = OrderDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(errors), 5)
        self.assertEqual(str(errors['contact_email'][0]), 'This field is required.')
        self.assertEqual(str(errors['shipping_address_line1'][0]), 'This field is required.')
        self.assertEqual(str(errors['shipping_city'][0]), 'This field is required.')
        self.assertEqual(str(errors['shipping_country'][0]), 'This field is required.')
        self.assertEqual(str(errors['shipping_zip'][0]), 'This field is required.')

        data['contact_email'] = ''
        data['shipping_address_line1'] = ''
        data['shipping_city'] = ''
        data['shipping_country'] = ''
        data['shipping_zip'] = ''

        serializer = OrderDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['contact_email'][0]), 'This field may not be blank.')
        self.assertEqual(str(errors['shipping_address_line1'][0]), 'This field may not be blank.')
        self.assertEqual(str(errors['shipping_city'][0]), 'This field may not be blank.')
        self.assertEqual(str(errors['shipping_country'][0]), 'This field may not be blank.')
        self.assertEqual(str(errors['shipping_zip'][0]), 'This field may not be blank.')

        data['contact_email'] = 'emailaddress'
        data['shipping_address_line1'] = 'A very loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong text'
        data['shipping_city'] = 'A very loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong text'
        data['shipping_country'] = 'A very loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong text'
        data['shipping_zip'] = 'A very loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong text'
        serializer = OrderDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['contact_email'][0]), 'Enter a valid email address.')
        self.assertEqual(str(errors['shipping_address_line1'][0]), 'Ensure this field has no more than 100 characters.')
        self.assertEqual(str(errors['shipping_city'][0]), 'Ensure this field has no more than 100 characters.')
        self.assertEqual(str(errors['shipping_country'][0]), 'Ensure this field has no more than 100 characters.')
        self.assertEqual(str(errors['shipping_zip'][0]), 'Ensure this field has no more than 100 characters.')

        data['contact_email'] = 'johndoe@example.com'
        data['shipping_address_line1'] = '123 Main St'
        data['shipping_city'] = 'Anytown'
        data['shipping_country'] = 'USA'
        data['shipping_zip'] = '12345'
        
        serializer = OrderDataSerializer(data=data)
        self.assertTrue(serializer.is_valid())

# class CartItemSerializerTestCase(TestCase):
    # def test_instance_validation(self):
        # Basic validations based on demo_product