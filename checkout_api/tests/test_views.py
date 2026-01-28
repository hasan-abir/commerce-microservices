from django.test import TestCase, Client
from checkout_api.models import Product, Cart, CartItem, Order, OrderItem
from checkout_api.serializers import ProductSerializer, CartSerializer, CartItemSerializer
from decimal import *
from django.urls import reverse
from unittest.mock import patch
from django.http import QueryDict
from django.test import TransactionTestCase
import redis

rd_instance = redis.Redis(host='redis', port=6379, decode_responses=True)

class ProductViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(name="Test Product", price=22.45, stock=8, is_active=True)
    def test_retrieve(self):
        response = self.client.get(f'/api/products/{self.product.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['url'])
        self.assertEqual(response.json()['name'], self.product.name)
        self.assertEqual(response.json()['price'], str(self.product.price))
        self.assertEqual(response.json()['is_active'], self.product.is_active)
    def test_list(self):
        product2 = Product.objects.create(name="Test Product2", price=22.45, stock=8, is_active=True)
        product3 = Product.objects.create(name="Test Product3", price=22.45, stock=8, is_active=True)

        response = self.client.get(f'/api/products/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)
        self.assertEqual(response.json()['results'][0]['name'], self.product.name)
        self.assertEqual(response.json()['results'][1]['name'], product2.name)
        self.assertEqual(response.json()['results'][2]['name'], product3.name)

class CartViewTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = Client()
    def test_list(self):
        response = self.client.get('/api/carts/')

        self.assertTrue(response.status_code, 200)

        self.assertEqual(response.json()['url'], f'http://testserver/api/carts/{1}/')
        self.assertTrue(response.json()['session_key'])
        self.assertEqual(response.json()['total'], Decimal(0.0))
        self.assertEqual(response.json()['subtotal'], Decimal(0.0))

        carts = Cart.objects.all()

        self.assertEqual(len(carts), 1)

        response = self.client.get('/api/carts/')

        self.assertEqual(len(carts), 1)

        response = self.client.get('/api/carts/')

        self.assertEqual(len(carts), 1)

        old_cart = carts.first()
        old_cart.status = Cart.COMPLETED
        old_cart.save()

        response = self.client.get('/api/carts/')
        
        carts = Cart.objects.all()

        self.assertEqual(len(carts), 2)


    def test_retrieve(self):
        response = self.client.get('/api/carts/')

        response = self.client.get(response.json()['url'])

        self.assertTrue(response.status_code, 200)

        self.assertEqual(response.json()['url'], f'http://testserver/api/carts/{1}/')
        self.assertTrue(response.json()['session_key'])
        self.assertEqual(response.json()['total'], Decimal(0.0))
        self.assertEqual(response.json()['subtotal'], Decimal(0.0))

class CartItemViewSetTestCase(TestCase):
    def setUp(self):
        rd_instance.flushdb()
        self.client = Client()

        self.product1 = Product.objects.create(name="Test Product", price=22.45, stock=8, is_active=True)
        self.cart1 = Cart.objects.create(session_key="123")
        self.cartItem1 = CartItem.objects.create(cart=self.cart1, product=self.product1, quantity=4)

        self.product2 = Product.objects.create(name="Test Product 1", price=22.45, stock=8, is_active=True)
        self.cart2 = Cart.objects.create(session_key="132")
        self.cartItem2 = CartItem.objects.create(cart=self.cart2, product=self.product2, quantity=2)

        self.product3 = Product.objects.create(name="Test Product 3", price=22.45, stock=8, is_active=True)

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

        product = reverse('product-detail', kwargs={'pk': self.product3.pk})

        data = {
            "quantity": 1,
            "product": product,
        }

        response = self.client.post('/api/cartitems/', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['msg'], 'Create your cart first.')

        self.client.get('/api/carts/')

        response = self.client.post('/api/cartitems/', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['msg'], "Specify a 'Idempotency-Key' attribute in the headers with a UUID")

        fake_product = reverse('product-detail', kwargs={'pk': 123})
        data['product'] = fake_product

        response = self.client.post('/api/cartitems/', data=data, headers={'Idempotency-Key': 'test-id-123'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['product'], ['Invalid hyperlink - Object does not exist.'])

        response = self.client.post('/api/cartitems/', data=data, headers={'Idempotency-Key': 'test-id-123'})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['msg'], "Duplicate request detected")

        self.product3.stock = 0
        self.product3.save()

        data['product'] = product

        response = self.client.post('/api/cartitems/', data=data, headers={'Idempotency-Key': 'test-id-124'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['msg'], f'{self.product3.name}: Out of stock')

        self.product3.stock = 1
        self.product3.save()

        response = self.client.post('/api/cartitems/', data=data, headers={'Idempotency-Key': 'test-id-125'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['product'], f'http://testserver/api/products/{self.product3.pk}/')
        self.assertTrue(response.json()['cart'])

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

class OrderViewSetTestCase(TestCase):
    def setUp(self):
        rd_instance.flushdb()
        self.client = Client()

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
    def test_get_detail(self):
        url = f'/api/orders/{self.order.pk}/'

        response = self.client.get('/api/orders/123/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['source_cart_session_key'], self.order.source_cart_session_key)
    @patch("checkout_api.views.placeorder_task")
    def test_post(self, mock_task):
        url = '/api/orders/'

        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['msg'], 'Create your cart first.')

        self.client.get('/api/carts/')

        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['msg'], "Specify a 'Idempotency-Key' attribute in the headers with a UUID")

        response = self.client.post(url, headers={'Idempotency-Key': 'test-id-123'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['msg'], 'Add items to your cart first.')

        response = self.client.post(url, headers={'Idempotency-Key': 'test-id-123'})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['msg'], "Duplicate request detected")

        product = Product.objects.create(name="Test Product 1", price=22.45, stock=8, is_active=True)
        product1 = Product.objects.create(name="Test Product 2", price=22.45, stock=8, is_active=True)
        cart = Cart.objects.first()
        CartItem.objects.create(cart=cart, product=product, quantity=2)
        CartItem.objects.create(cart=cart, product=product1, quantity=1)

        response = self.client.post(url, data={}, headers={'Idempotency-Key': 'test-id-124'})
        self.assertEqual(response.status_code, 400)

        data = {'contact_email': 'johndoe@example.com',
            'shipping_address_line1': '123 Main St',
            'shipping_city': 'Anytown',
            'shipping_country': 'USA',
            'shipping_zip': '12345'}
        product.stock = 0
        product.save()

        response = self.client.post(url, data=data, headers={'Idempotency-Key': 'test-id-125'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['msg'], f"{product.name}: Out of stock")

        cartItems = CartItem.objects.filter(cart=cart.pk)

        self.assertEqual(len(cartItems), 1)

        response = self.client.post(url, data=data, headers={'Idempotency-Key': 'test-id-126'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['msg'], "Success! We've accepted your order request and are dispatching the products now.")
        mock_task.delay.assert_called_once()

        expected = QueryDict('', mutable=True)

        expected.update({
            'contact_email': data['contact_email'],
            'shipping_address_line1': data['shipping_address_line1'],
            'shipping_city': data['shipping_city'],
            'shipping_country': data['shipping_country'],
            'shipping_zip': data['shipping_zip'],
            'session_key': cart.session_key
        })

        mock_task.delay.assert_called_with(expected)

        saved_product = Product.objects.get(pk=product.pk)
        self.assertEqual(saved_product.stock, 0)

        saved_cart = Cart.objects.get(pk=cart.pk)
        self.assertEqual(saved_cart.status, Cart.PROCESSING)

class OrderItemViewSetTestCase(TestCase):
    def setUp(self):
        self.client = Client()

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

    def test_get_detail(self):
        url = f'/api/orderitems/{self.order_item.pk}/'

        response = self.client.get('/api/orderitems/123/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['unit_price'], str(self.order_item.unit_price))

class PaymentViewSetTestCase(TestCase):
    @patch("checkout_api.views.stripe.PaymentIntent.create")
    def test_post(self, mock_stripe):
        mock_stripe.return_value = {
            'client_secret': '123',
        }

        url = '/api/payments/'

        data = {}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['msg'], "Specify a 'Idempotency-Key' attribute in the headers with a UUID")


        response = self.client.post(url, data, headers={'Idempotency-Key': 'test-id-127'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['total'][0], 'This field is required.')

        data['total'] = 12.34

        response = self.client.post(url, data, headers={'Idempotency-Key': 'test-id-128'})

        self.assertEqual(response.status_code, 200)

        mock_stripe.assert_called_once()

        mock_stripe.assert_called_with(amount= str(data['total']),
            currency= 'usd')
    