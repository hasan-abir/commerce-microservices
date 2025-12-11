from django.test import TestCase
from checkout_api.models import Product, Cart, CartItem, Order, OrderItem
from decimal import *

class ProductTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Test Product", price=22.45, stock=8, is_active=True)

    def test_instance_is_properly_saved(self):
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.get(name=self.product.name)

        self.assertEqual(product.name, self.product.name)
        self.assertEqual(product.price, round(Decimal(self.product.price), 2))
        self.assertEqual(product.stock, self.product.stock)
        self.assertEqual(product.is_active, self.product.is_active)

    def test_str_method(self):
        product = Product.objects.get(name=self.product.name)

        self.assertEqual(product.__str__(), self.product.name)


class CartTestCase(TestCase):
    def setUp(self):
        self.cart = Cart.objects.create(session_key="123")

    def test_instance_is_properly_saved(self):
        self.assertEqual(Cart.objects.count(), 1)
        cart = Cart.objects.get(session_key=self.cart.session_key)

        self.assertEqual(cart.session_key, self.cart.session_key)

    def test_str_method(self):
        cart = Cart.objects.get(session_key=self.cart.session_key)

        self.assertEqual(cart.__str__(), f"User: {self.cart.session_key}")

class CartItemTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Test Product", price=22.45, stock=8, is_active=True)
        self.cart = Cart.objects.create(session_key="123")
        self.cartItem = CartItem.objects.create(cart=self.cart, product=self.product, quantity=4)

    def test_instance_is_properly_saved(self):
        self.assertEqual(CartItem.objects.count(), 1)
        cartItem = CartItem.objects.get(quantity=self.cartItem.quantity)

        self.assertEqual(cartItem.product.name, self.cartItem.product.name)
        self.assertEqual(cartItem.cart.session_key, self.cartItem.cart.session_key)
        self.assertEqual(cartItem.quantity, self.cartItem.quantity)

    def test_str_method(self):
        cartItem = CartItem.objects.get(quantity=self.cartItem.quantity)

        self.assertEqual(cartItem.__str__(), f"Belongs to cart: {self.cartItem.cart.session_key}")

class OrderTestCase(TestCase):
    def setUp(self):
        self.order = Order.objects.create(status=Order.PAID,
            total=Decimal('45.99'),
            subtotal=Decimal('42.00'),
            tax_rate=Decimal('0.095'),
            contact_email='johndoe@example.com',
            shipping_address_line1='123 Main St',
            shipping_city='Anytown',
            shipping_country='USA',
            shipping_zip='12345',
            source_cart_session_key='session_key_1234567890abcdef')

    def test_instance_is_properly_saved(self):
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.create(status=Order.PAID,
            total=Decimal('45.99'),
            subtotal=Decimal('42.00'),
            tax_rate=Decimal('0.095'),
            contact_email='johndoe@example.com',
            shipping_address_line1='123 Main St',
            shipping_city='Anytown',
            shipping_country='USA',
            shipping_zip='12345',
            source_cart_session_key='session_key_1234567890abcdef')
        
        self.assertTrue(order.order_number.startswith('ORD-'))
        self.assertEqual(order.total, self.order.total)
        self.assertEqual(order.subtotal, self.order.subtotal)
        self.assertEqual(order.tax_rate, self.order.tax_rate)
        self.assertEqual(order.contact_email, self.order.contact_email)
        self.assertEqual(order.shipping_address_line1, self.order.shipping_address_line1)
        self.assertEqual(order.shipping_city, self.order.shipping_city)
        self.assertEqual(order.shipping_country, self.order.shipping_country)
        self.assertEqual(order.shipping_zip, self.order.shipping_zip)
        self.assertEqual(order.source_cart_session_key, self.order.source_cart_session_key)

    def test_str_method(self):
        order = Order.objects.get(order_number=self.order.order_number)

        self.assertEqual(order.__str__(), f"Order number: {self.order.order_number}")


class OrderItemTestCase(TestCase):
    def setUp(self):
        self.order = Order.objects.create(status=Order.PAID,
            total=Decimal('45.99'),
            subtotal=Decimal('42.00'),
            tax_rate=Decimal('0.095'),
            contact_email='johndoe@example.com',
            shipping_address_line1='123 Main St',
            shipping_city='Anytown',
            shipping_country='USA',
            shipping_zip='12345',
            source_cart_session_key='session_key_1234567890abcdef')

        self.order_item = OrderItem.objects.create(order=self.order, original_product_id=1, product_name="New Product", unit_price = Decimal('1.23'), quantity=3)

    def test_instance_is_properly_saved(self):
        self.assertEqual(OrderItem.objects.count(), 1)
        order_item = OrderItem.objects.create(order=self.order, original_product_id=1, product_name="New Product", unit_price = Decimal('1.23'), quantity=3)
        
        self.assertEqual(order_item.order.order_number, self.order.order_number)
        self.assertEqual(order_item.original_product_id, self.order_item.original_product_id)
        self.assertEqual(order_item.product_name, self.order_item.product_name)
        self.assertEqual(order_item.unit_price, self.order_item.unit_price)
        self.assertEqual(order_item.quantity, self.order_item.quantity)

    def test_str_method(self):
        order_item = OrderItem.objects.get(product_name=self.order_item.product_name)

        self.assertEqual(order_item.__str__(), f"Order item for order: {self.order.order_number}")

