from checkout_api.services import placeorder_service, cleanupcarts_service
from django.test import TestCase
from checkout_api.models import Cart, CartItem, Product, Order, OrderItem
from decimal import *
from unittest.mock import patch, ANY
from django.utils import timezone
from datetime import timedelta

class PlaceOrderServiceTestCase(TestCase):
    def setUp(self):
        self.cart = Cart.objects.create(session_key="123")
        self.product1 = Product.objects.create(name="Test Product", price=22.45, stock=8, is_active=True)
        self.product2 = Product.objects.create(name="Test Product 2", price=20.45, stock=8, is_active=True)
        self.cartItem1 = CartItem.objects.create(cart=self.cart, product=self.product1, quantity=4)
        self.cartItem2 = CartItem.objects.create(cart=self.cart, product=self.product2, quantity=2)
    @patch('checkout_api.services.sendmail_service')
    def test_method(self, mock_service):
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

        savedCart = Cart.objects.get(pk=self.cart.pk)

        self.assertEqual(savedCart.status, Cart.COMPLETED)

        mock_service.assert_called_once()
        mock_service.assert_called_with({
            'recipient': data['contact_email'],
            'subject': ANY,
            'msg_content': ANY
        })

    @patch('checkout_api.models.Order.objects.create')
    def test_fail_method(self, mock_create):
        mock_create.side_effect = Exception("The database is lit, bruv!")

        data = {'contact_email': 'johndoe@example.com',
            'shipping_address_line1': '123 Main St',
            'shipping_city': 'Anytown',
            'shipping_country': 'USA',
            'shipping_zip': '12345',
            'session_key': self.cart.session_key}

        with self.assertRaises(Exception):
            placeorder_service(data)
            
        cart = Cart.objects.get(pk=self.cart.pk)
        self.assertEqual(cart.status, Cart.FAILED)
                 
class CleanupCartServiceTestCase(TestCase):
    def test_return(self):
        cart1 = Cart.objects.create(session_key='1')
        cart2 = Cart.objects.create(session_key='2')
        cart3 = Cart.objects.create(session_key='3')
        cart4 = Cart.objects.create(session_key='4', status=Cart.PROCESSING)
        cart5 = Cart.objects.create(session_key='5', status=Cart.COMPLETED)
        cart6 = Cart.objects.create(session_key='6', status=Cart.FAILED)
        cart7 = Cart.objects.create(session_key='7', status=Cart.FAILED)
        cart8 = Cart.objects.create(session_key='8', status=Cart.COMPLETED)
        cart9 = Cart.objects.create(session_key='9', status=Cart.PROCESSING)
        cart10 = Cart.objects.create(session_key='10', status=Cart.COMPLETED)
        cart11 = Cart.objects.create(session_key='11', status=Cart.COMPLETED)

        three_days_ago = timezone.now() - timedelta(days=3)
        Cart.objects.filter(id__in=[cart2.id, cart3.id, cart7.id, cart8.id, cart9.id]).update(created_at=three_days_ago, updated_at=three_days_ago)
        
        ninety_one_days_ago = timezone.now() - timedelta(days=91)
        Cart.objects.filter(id__in=[cart10.id, cart11.id]).update(created_at=ninety_one_days_ago, updated_at=ninety_one_days_ago)
        
        
        count = cleanupcarts_service()

        self.assertEqual(count, 5)

        self.assertTrue(Cart.objects.filter(id__in=[cart1.pk, cart4.pk, cart5.pk, cart6.pk, cart8.pk, cart9.pk]).exists())
        self.assertFalse(Cart.objects.filter(id__in=[cart2.pk, cart3.pk, cart7.pk, cart10.pk, cart11.pk]).exists())