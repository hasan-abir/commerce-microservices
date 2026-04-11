from django.test import TestCase
from checkout_api.models import Order, OrderItem
from decimal import *

class OrderTestCase(TestCase):
    def setUp(self):
        self.order = Order.objects.create(status=Order.PAID,
            total=4599,
            contact_email='johndoe@example.com',
            payment_intent_id='123')

    def test_instance_is_properly_saved(self):
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.create(status=Order.PAID,
            total=4599,
            contact_email='johndoe@example.com',
            payment_intent_id='231')
        
        self.assertTrue(order.order_number.startswith('ORD-'))
        self.assertEqual(order.total, self.order.total)
        self.assertEqual(order.contact_email, self.order.contact_email)
        self.assertTrue(order.payment_intent_id)

    def test_save_method(self):
        order = Order.objects.create(status=Order.PAID,
            total=4599,
            contact_email='johndoe@example.com',
            payment_intent_id='321')
        
        self.assertNotEqual(self.order.order_number, order.order_number)

    def test_str_method(self):
        order = Order.objects.get(order_number=self.order.order_number)

        self.assertEqual(order.__str__(), f"Order number: {self.order.order_number}")

class OrderItemTestCase(TestCase):
    def setUp(self):
        self.order = Order.objects.create(status=Order.PAID,
            total=4599,
            contact_email='johndoe@example.com',
            payment_intent_id='123')
        self.order_item = OrderItem.objects.create(item_id='1', price=1200, quantity=4, title='test', order=self.order)

    def test_instance_is_properly_saved(self):
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_str_method(self):
        self.assertEqual(self.order_item.__str__(), f"Order item: {self.order_item.item_id}")
