from django.test import TestCase
from checkout_api.models import Product, Cart, CartItem, Order, OrderItem, PaymentIntent
from checkout_api.serializers import ProductSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, OrderDataSerializer, PaymentSerializer, PaymentIntentSerializer
from decimal import *
from django.urls import reverse
from django.test.client import RequestFactory

class ProductSerializerTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Test Product", price=22.45, stock=8, is_active=True)
    def test_instance_validation(self):
        # Null validation
        serializer = ProductSerializer(data={})
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 4)
        self.assertEqual(str(errors['name'][0]), "This field is required.")
        self.assertEqual(str(errors['price'][0]), "This field is required.")
        self.assertEqual(str(errors['stock'][0]), "This field is required.")
        self.assertEqual(str(errors['is_active'][0]), "This field is required.")

        # Blank validation
        data = {
            "name": "",
            "price": 0,
            "stock": 0,
            "is_active": False
        }

        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 3)
        self.assertEqual(str(errors['name'][0]), "This field may not be blank.")
        self.assertEqual(str(errors['price'][0]), "Ensure this value is greater than or equal to 0.01.")
        self.assertEqual(str(errors['stock'][0]), "Ensure this value is greater than or equal to 1.")

        # Text limit validation
        data["name"] = "A very loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong text"
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['name'][0]), "Ensure this field has no more than 100 characters.")

        # Price validation
        data["price"] = 100000000000000000.01
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['price'][0]), "Ensure that there are no more than 10 digits in total.")

        # Successful validation
        data = {
            "name": self.product.name,
            "price": self.product.price,
            "stock": self.product.stock,
            "is_active": self.product.is_active,
        }
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())

class CartSerializerTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.cart = Cart.objects.create(session_key="123")

        self.product1 = Product.objects.create(name="Test Product 1", price=22.45, stock=8, is_active=True)
        self.product2 = Product.objects.create(name="Test Product 2", price=22.45, stock=2, 
        is_active=True)
        self.cartItem1 = CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        self.cartItem2 = CartItem.objects.create(cart=self.cart, product=self.product2, quantity=3)

    def test_instance_validation(self):
        # Null validation
        serializer = CartSerializer(data={})
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(str(errors['session_key'][0]), "This field is required.")

        # Blank validation
        data = {
            "session_key": "",
        }

        serializer = CartSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(str(errors['session_key'][0]), "This field may not be blank.")

        # Unique validation
        data["session_key"] = "123"
        serializer = CartSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['session_key'][0]), "Cart with this session key already exists.")

        # Successful validation
        data = {
            "session_key": "321",
        }
        serializer = CartSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        mock_request = self.factory.get('/api/cart/')
        serializer = CartSerializer(self.cart, context={'request': mock_request})
        self.assertTrue(serializer.data['url'])
        self.assertTrue(serializer.data['session_key'], data['session_key'])
        self.assertTrue(serializer.data['total'], Decimal('121.23'))
        self.assertTrue(serializer.data['subtotal'], Decimal('112.25'))

class CartItemSerializerTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.product = Product.objects.create(name="Test Product", price=22.45, stock=8, is_active=True)
        self.product1 = Product.objects.create(name="Test Product 1", price=22.45, stock=8, is_active=True)
        self.cart = Cart.objects.create(session_key="123")
        self.cartItem = CartItem.objects.create(cart=self.cart, product=self.product, quantity=4)
    def test_instance_validation(self):
        # Null validation
        serializer = CartItemSerializer(data={})
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 2)
        self.assertEqual(str(errors['quantity'][0]), "This field is required.")
        self.assertEqual(str(errors['product'][0]), "This field is required.")

        # Blank validation
        data = {
            "quantity": 0,
        }

        serializer = CartItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 2)
        self.assertEqual(str(errors['quantity'][0]), "Ensure this value is greater than or equal to 1.")

        # Success
        product = reverse('product-detail', kwargs={'pk': self.product1.pk})
        cart = reverse('cart-detail', kwargs={'pk': self.cart.pk})
        data = {
            "quantity": 1,
            "product": product,
            "cart": cart
        }
        mock_request = self.factory.get('/api/cartitems/')

        serializer = CartItemSerializer(data=data, context={'request': mock_request})
        self.assertTrue(serializer.is_valid())
        saved_instance = serializer.save()

        serializer = CartItemSerializer(instance=saved_instance, context={'request': mock_request})
        self.assertTrue(serializer.data['url'])
        self.assertTrue(serializer.data['cart'], data['cart'])
        self.assertTrue(serializer.data['product'], data['product'])
        self.assertTrue(serializer.data['quantity'], data['quantity'])

        serializer = CartItemSerializer(data=data, context={'request': mock_request})
        self.assertFalse(serializer.is_valid())

class OrderSerializerTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

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
    def test_instance_validation(self):
        # Null validation
        serializer = OrderSerializer(data={})
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 9)
        self.assertEqual(str(errors['source_cart_session_key'][0]), "This field is required.")
        self.assertEqual(str(errors['total'][0]), "This field is required.")
        self.assertEqual(str(errors['subtotal'][0]), "This field is required.")
        self.assertEqual(str(errors['tax_rate'][0]), "This field is required.")
        self.assertEqual(str(errors['contact_email'][0]), "This field is required.")
        self.assertEqual(str(errors['shipping_address_line1'][0]), "This field is required.")
        self.assertEqual(str(errors['shipping_city'][0]), "This field is required.")
        self.assertEqual(str(errors['shipping_country'][0]), "This field is required.")
        self.assertEqual(str(errors['shipping_zip'][0]), "This field is required.")

        # Blank validation
        data = {
            "source_cart_session_key": "",
            "total": Decimal('0.00'),
            "subtotal": Decimal('0.00'),
            "tax_rate": Decimal('0.00'),
            "contact_email": "",
            "shipping_address_line1": "",
            "shipping_city": "",
            "shipping_country": "",
            "shipping_zip": "",
        }

        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 9)
        self.assertEqual(str(errors['total'][0]), "Ensure this value is greater than or equal to 0.01.")
        self.assertEqual(str(errors['subtotal'][0]), "Ensure this value is greater than or equal to 0.01.")
        self.assertEqual(str(errors['tax_rate'][0]), "Ensure this value is greater than or equal to 0.01.")
        self.assertEqual(str(errors['source_cart_session_key'][0]), "This field may not be blank.")
        self.assertEqual(str(errors['contact_email'][0]), "This field may not be blank.")
        self.assertEqual(str(errors['shipping_address_line1'][0]), "This field may not be blank.")
        self.assertEqual(str(errors['shipping_city'][0]), "This field may not be blank.")
        self.assertEqual(str(errors['shipping_country'][0]), "This field may not be blank.")
        self.assertEqual(str(errors['shipping_zip'][0]), "This field may not be blank.")

        # Choices validation
        data['status'] = 'something'
        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['status'][0]), '"something" is not a valid choice.')

        # Success
        data = {
            'status': Order.PAID,
            'total': Decimal('45.99'),
            'subtotal': Decimal('42.00'),
            'tax_rate': Decimal('0.095'),
            'contact_email': 'johndoe@example.com',
            'shipping_address_line1': '123 Main St',
            'shipping_city': 'Anytown',
            'shipping_country': 'USA',
            'shipping_zip': '12345',
            'source_cart_session_key': 'session_key_1234567890abcdef'
        }

        serializer = OrderSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        mock_request = self.factory.get('/api/orders/')

        serializer = OrderSerializer(data=data, context={'request': mock_request})
        self.assertTrue(serializer.is_valid())
        saved_instance = serializer.save()

        serializer = OrderSerializer(instance=saved_instance, context={'request': mock_request})

        self.assertTrue(serializer.data['url'])
        self.assertTrue(serializer.data['order_number'])
        self.assertEqual(serializer.data['total'], str(data['total']))
        self.assertEqual(serializer.data['subtotal'], str(data['subtotal']))
        self.assertEqual(serializer.data['tax_rate'], str(data['tax_rate']))
        self.assertEqual(serializer.data['status'], data['status'])
        self.assertTrue(serializer.data['date_placed'])
        self.assertEqual(serializer.data['source_cart_session_key'], data['source_cart_session_key'])
        self.assertEqual(serializer.data['contact_email'], data['contact_email'])
        self.assertEqual(serializer.data['shipping_address_line1'], data['shipping_address_line1'])
        self.assertEqual(serializer.data['shipping_city'], data['shipping_city'])
        self.assertEqual(serializer.data['shipping_country'], data['shipping_country'])
        self.assertEqual(serializer.data['shipping_zip'], data['shipping_zip'])

class OrderItemSerializerTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

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
    def test_instance_validation(self):
        # Null validation
        serializer = OrderItemSerializer(data={})
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 5)
        self.assertEqual(str(errors['original_product_id'][0]), "This field is required.")
        self.assertEqual(str(errors['product_name'][0]), "This field is required.")
        self.assertEqual(str(errors['unit_price'][0]), "This field is required.")
        self.assertEqual(str(errors['quantity'][0]), "This field is required.")
        self.assertEqual(str(errors['order'][0]), "This field is required.")

        # # Blank validation
        data = {
            "original_product_id": 1,
            "product_name": "",
            "unit_price": Decimal('0.00'),
            "quantity": 0,
            "order": "",
        }

        serializer = OrderItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 4)
        self.assertEqual(str(errors['product_name'][0]), "This field may not be blank.")
        self.assertEqual(str(errors['unit_price'][0]), "Ensure this value is greater than or equal to 0.01.")
        self.assertEqual(str(errors['quantity'][0]), "Ensure this value is greater than or equal to 1.")
        self.assertEqual(str(errors['order'][0]), "This field may not be null.")

        mock_request = self.factory.get('/api/orders/')
        order = reverse(viewname='order-detail', kwargs={'pk': self.order.pk})
        data = {
            "original_product_id": 1,
            "product_name": "Product",
            "unit_price": Decimal('1.34'),
            "quantity": 4,
            "order": order,
        }

        serializer = OrderItemSerializer(data=data, context={'request': mock_request})
        self.assertTrue(serializer.is_valid())

        serializer = OrderItemSerializer(data=data, context={'request': mock_request})
        self.assertTrue(serializer.is_valid())
        saved_instance = serializer.save()

        serializer = OrderItemSerializer(instance=saved_instance, context={'request': mock_request})

        self.assertTrue(serializer.data['url'])
        self.assertEqual(serializer.data['unit_price'], str(data['unit_price']))
        self.assertEqual(serializer.data['quantity'], data['quantity'])
        self.assertEqual(serializer.data['original_product_id'], data['original_product_id'])
        self.assertEqual(serializer.data['product_name'], data['product_name'])
        self.assertEqual(serializer.data['order'], 'http://testserver' + order)

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

class PaymentSerializerTestCase(TestCase):
    def test_instance_validation(self):
        data = {}

        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        errors = serializer.errors
        self.assertEqual(str(errors['total'][0]), 'This field is required.')

        data = {'total': 0.00}

        serializer = PaymentSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())

        errors = serializer.errors
        self.assertEqual(str(errors['total'][0]), 'Ensure this value is greater than or equal to 0.01.')

        data['total'] = 12.34

        serializer = PaymentSerializer(data=data)
        self.assertTrue(serializer.is_valid())

class PaymentIntentSerializerTestCase(TestCase):
    def test_instance_validation(self):
        data = {}

        serializer = PaymentIntentSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        errors = serializer.errors
        self.assertEqual(str(errors['amount'][0]), 'This field is required.')
        self.assertEqual(str(errors['currency'][0]), 'This field is required.')
        self.assertEqual(str(errors['order_id'][0]), 'This field is required.')
        self.assertEqual(str(errors['payment_intent_id'][0]), 'This field is required.')

        data['amount'] = 0.00

        serializer = PaymentIntentSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())

        errors = serializer.errors
        self.assertEqual(str(errors['amount'][0]), 'Ensure this value is greater than or equal to 0.01.')

        data['status'] = "Somethin"

        serializer = PaymentIntentSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())

        errors = serializer.errors
        self.assertEqual(str(errors['status'][0]), f'"{data['status']}" is not a valid choice.')

        data['amount'] = 12.34
        data['status'] = PaymentIntent.SUCCEEDED
        data['currency'] = "usd"
        data['order_id'] = "123"
        data['payment_intent_id'] = "123"
        data['payment_method_id'] = "123"

        serializer = PaymentIntentSerializer(data=data)
        self.assertTrue(serializer.is_valid())