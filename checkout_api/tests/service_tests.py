from checkout_api.services import placeorder_service
from django.test import TestCase
from checkout_api.models import Cart, CartItem, Product, Order, OrderItem
from decimal import *

class PlaceOrderServiceTestCase(TestCase):
    def setUp(self):
        self.cart = Cart.objects.create(session_key="123")
        self.product1 = Product.objects.create(name="Test Product", price=22.45, stock=8, is_active=True)
        self.product2 = Product.objects.create(name="Test Product 2", price=20.45, stock=8, is_active=True)
        self.cartItem1 = CartItem.objects.create(cart=self.cart, product=self.product1, quantity=4)
        self.cartItem2 = CartItem.objects.create(cart=self.cart, product=self.product2, quantity=2)
        
    def test_method(self):
        data = {'contact_email': 'johndoe@example.com',
            'shipping_address_line1': '123 Main St',
            'shipping_city': 'Anytown',
            'shipping_country': 'USA',
            'shipping_zip': '12345',
            'session_key': self.cart.session_key}

        placeorder_service(data)

        cartItems = CartItem.objects.all()
        orders = Order.objects.all()
        self.assertEqual(len(cartItems), 0)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].contact_email, data['contact_email'])
        self.assertEqual(orders[0].shipping_address_line1, data['shipping_address_line1'])
        self.assertEqual(orders[0].shipping_city, data['shipping_city'])
        self.assertEqual(orders[0].shipping_country, data['shipping_country'])
        self.assertEqual(orders[0].shipping_zip, data['shipping_zip'])
        self.assertEqual(orders[0].source_cart_session_key, self.cart.session_key)
        self.assertEqual(orders[0].total, Decimal('141.16'))
        self.assertEqual(orders[0].subtotal, Decimal('130.70'))
        self.assertEqual(orders[0].tax_rate, Decimal('0.08'))
        self.assertEqual(orders[0].status, Order.PENDING)
        
        orderItems = OrderItem.objects.all()
        self.assertEqual(len(orderItems), 2)
        self.assertEqual(orderItems[0].original_product_id, self.product1.pk )
        self.assertEqual(orderItems[0].product_name, self.product1.name )
        self.assertEqual(str(orderItems[0].unit_price), str(self.product1.price) )
        self.assertEqual(orderItems[0].quantity, self.cartItem1.quantity )
        self.assertEqual(orderItems[1].original_product_id, self.product2.pk )
        self.assertEqual(orderItems[1].product_name, self.product2.name )
        self.assertEqual(str(orderItems[1].unit_price), str(self.product2.price) )
        self.assertEqual(orderItems[1].quantity, self.cartItem2.quantity )
            
