from checkout_api.services import placeorder_service
from django.test import TestCase
from checkout_api.models import Cart, CartItem, Product

class PlaceOrderServiceTestCase(TestCase):
    def setUp(self):
        self.cart = Cart.objects.create(session_key="123")
        self.product = Product.objects.create(name="Test Product", price=22.45, stock=8, is_active=True)
        self.cartItem = CartItem.objects.create(cart=self.cart, product=self.product, quantity=4)
        
    def test_instance_validation(self):
        data = {
            'session_key': self.cart.session_key
        }
        placeorder_service(data)
        