from django.test import TestCase, Client
from checkout_api.models import Product, Cart, CartItem
from checkout_api.serializers import ProductSerializer, CartSerializer, CartItemSerializer
from decimal import *

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
    def test_retrieve(self):
        response = self.client.get(f'/api/carts/')

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
        self.assertEqual(response.json()['results'][0]['cart'], self.cartItem1.cart.pk)
        self.assertEqual(response.json()['results'][1]['cart'], self.cartItem2.cart.pk)

    # def test_get_detail(self):
    #     url = f'/api/cart-items/{self.firstPost.pk}/'

    #     response = self.client.get('/api/cart-items/123/')
    #     self.assertEqual(response.status_code, 404)

    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json()['title'], self.firstPost.title)

    # def test_post(self):
    #     response = self.client.post('/api/cart-items/')
    #     self.assertEqual(response.status_code, 401)

    #     self.login()

    #     data = {"title": "New post", "content": "New post content", "published_date": "2025-10-04"}

    #     response = self.client.post('/api/cart-items/', data=data, headers=self.tokenHeader)
    #     self.assertEqual(response.json()['title'], data["title"])
    #     self.assertTrue(response.json()['author'])
    #     self.assertEqual(response.status_code, 201)

    # def test_put(self):
    #     url = f'/api/cart-items/{self.firstPost.pk}/'

    #     response = self.client.put(url)
    #     self.assertEqual(response.status_code, 401)

    #     self.login(unauth=True)

    #     response = self.client.put('/api/cart-items/123/', headers=self.tokenHeader)
    #     self.assertEqual(response.status_code, 404)

    #     data = {"title": "New post", "content": "New post content", "published_date": "2025-10-04"}

    #     response = self.client.put(url, data=data, content_type="application/json", headers=self.tokenHeader)
    #     self.assertEqual(response.status_code, 403)

    #     self.login()

    #     response = self.client.put(url, data=data, content_type="application/json", headers=self.tokenHeader)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json()['title'], data["title"])
    #     self.assertTrue(response.json()['author'])

    # def test_patch(self):
    #     url = f'/api/cart-items/{self.firstPost.pk}/'

    #     response = self.client.patch(url)
    #     self.assertEqual(response.status_code, 401)

    #     self.login(unauth=True)

    #     response = self.client.patch('/api/cart-items/123/', headers=self.tokenHeader)
    #     self.assertEqual(response.status_code, 404)

    #     data = {"title": "New post"}

    #     response = self.client.patch(url, data=data, content_type="application/json", headers=self.tokenHeader)
    #     self.assertEqual(response.status_code, 403)

    #     self.login()

    #     response = self.client.patch(url, data=data, content_type="application/json", headers=self.tokenHeader)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json()['title'], data["title"])
    #     self.assertTrue(response.json()['author'])
        
    # def test_delete(self):
    #     url = f'/api/cart-items/{self.firstPost.pk}/'

    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, 401)

    #     self.login(unauth=True)

    #     response = self.client.delete('/api/cart-items/123/', headers=self.tokenHeader)
    #     self.assertEqual(response.status_code, 404)

    #     response = self.client.delete(url, headers=self.tokenHeader)
    #     self.assertEqual(response.status_code, 403)

    #     self.login()

    #     response = self.client.delete(url, headers=self.tokenHeader)
    #     self.assertEqual(response.status_code, 204)        

