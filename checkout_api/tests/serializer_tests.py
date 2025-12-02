from django.test import TestCase
from checkout_api.models import Product, Cart, CartItem
from checkout_api.serializers import ProductSerializer, CartSerializer, CartItemSerializer

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
        data["name"] = "This is very loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong text"
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
        self.cart = Cart.objects.create(session_key="123")
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

class CartItemSerializerTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Test Product", price=22.45, stock=8, is_active=True)
        self.cart = Cart.objects.create(session_key="123")
        self.cartItem = CartItem.objects.create(cart=self.cart, product=self.product, quantity=4)
    def test_instance_validation(self):
        # Null validation
        serializer = CartItemSerializer(data={})
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 3)
        self.assertEqual(str(errors['quantity'][0]), "This field is required.")
        self.assertEqual(str(errors['product'][0]), "This field is required.")
        self.assertEqual(str(errors['cart'][0]), "This field is required.")

        # Blank validation
        data = {
            "quantity": 0,
        }

        serializer = CartItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 3)
        self.assertEqual(str(errors['quantity'][0]), "Ensure this value is greater than or equal to 1.")

        # Successful validation - TODO
        data = {
            "quantity": 1,
            "product": self.product,
            "cart": self.cart
        }
        serializer = CartItemSerializer(data=data)

        # self.assertTrue(serializer.is_valid())