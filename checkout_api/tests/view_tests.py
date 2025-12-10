from django.test import TestCase, Client
from checkout_api.models import Product, Cart, CartItem
from checkout_api.serializers import ProductSerializer, CartSerializer, CartItemSerializer
from decimal import *
from django.urls import reverse

class ProductViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(name="Test Product", price=22.45, stock=8, is_active=True)
    def test_retrieve(self):
        response = self.client.get(f'/api/products/{self.product.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['url'])
        self.assertEqual(response.json()['id'], self.product.pk)
        self.assertEqual(response.json()['name'], self.product.name)
        self.assertEqual(response.json()['price'], str(self.product.price))
        self.assertEqual(response.json()['is_active'], self.product.is_active)

class CartViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    def test_list(self):
        response = self.client.get(f'/api/carts/')

        self.assertTrue(response.status_code, 200)

        self.assertEqual(response.json()['id'], 1)
        self.assertTrue(response.json()['session_key'])
        self.assertEqual(response.json()['total'], Decimal(0.0))
        self.assertEqual(response.json()['subtotal'], Decimal(0.0))
    def test_retrieve(self):
        response = self.client.get(f'/api/carts/')

        response = self.client.get(f'/api/carts/{response.json()['id']}/')

        self.assertTrue(response.status_code, 200)

        self.assertEqual(response.json()['id'], 1)
        self.assertTrue(response.json()['session_key'])
        self.assertEqual(response.json()['total'], Decimal(0.0))
        self.assertEqual(response.json()['subtotal'], Decimal(0.0))

class CartItemViewSetTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.product1 = Product.objects.create(name="Test Product", price=22.45, stock=8, is_active=True)
        self.cart1 = Cart.objects.create(session_key="123")
        self.cartItem1 = CartItem.objects.create(cart=self.cart1, product=self.product1, quantity=4)

        self.product2 = Product.objects.create(name="Test Product 1", price=22.45, stock=8, is_active=True)
        self.cart2 = Cart.objects.create(session_key="132")
        self.cartItem2 = CartItem.objects.create(cart=self.cart2, product=self.product2, quantity=2)

    def test_get_list(self):
        response = self.client.get('/api/cartitems/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(response.json()['results'][0]['cart'], f'http://testserver/api/carts/{self.cartItem1.cart.pk}/')
        self.assertEqual(response.json()['results'][1]['cart'], f'http://testserver/api/carts/{self.cartItem2.cart.pk}/')

    def test_get_detail(self):
        url = f'/api/cartitems/{self.cartItem1.pk}/'

        response = self.client.get('/api/cartitems/123/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['product'], f'http://testserver/api/products/{self.cartItem1.product.pk}/')

    def test_post(self):
        response = self.client.post('/api/cartitems/')
        self.assertEqual(response.status_code, 400)

        product = reverse('product-detail', kwargs={'pk': self.product1.pk})
        cart = reverse('cart-detail', kwargs={'pk': self.cart1.pk})
        data = {
            "quantity": 1,
            "product": product,
            "cart": cart
        }

        response = self.client.post('/api/cartitems/', data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['product'], f'http://testserver/api/products/{self.cartItem1.product.pk}/')

    def test_put(self):
        url = f'/api/cartitems/{self.cartItem1.pk}/'

        response = self.client.put(url)
        self.assertEqual(response.status_code, 400)

        response = self.client.put('/api/cartitems/123/')
        self.assertEqual(response.status_code, 404)

        product = reverse('product-detail', kwargs={'pk': self.product1.pk})
        cart = reverse('cart-detail', kwargs={'pk': self.cart1.pk})
        data = {
            "quantity": 1,
            "product": product,
            "cart": cart
        }

        response = self.client.put(url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['product'], f'http://testserver/api/products/{self.cartItem1.product.pk}/')

    def test_patch(self):
        url = f'/api/cartitems/{self.cartItem1.pk}/'

        response = self.client.patch('/api/cartitems/123/')
        self.assertEqual(response.status_code, 404)

        data = {"quantity": 2}

        response = self.client.patch(url, data=data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['quantity'], data["quantity"])
        
    def test_delete(self):
        url = f'/api/cartitems/{self.cartItem1.pk}/'

        response = self.client.delete('/api/cartitems/123/')
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)        

