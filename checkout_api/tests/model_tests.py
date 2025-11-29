from django.test import TestCase
from checkout_api.models import Product, Cart, CartItem
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

