from django.conf import settings
from django.core.mail import send_mail
from checkout_api.models import Cart, CartItem, Order, OrderItem
from checkout_api.serializers import CartSerializer
from decimal import *

def placeorder_service(data):
    session_key = data['session_key']

    cart = Cart.objects.get(session_key=session_key)
    cartSerializer = CartSerializer(instance=cart)
    cartItems = CartItem.objects.filter(cart__session_key=session_key)

    Order.objects.create(status=Order.PENDING, source_cart_session_key=session_key, total=cartSerializer.data['total'], subtotal=cartSerializer.data['subtotal'], tax_rate=Decimal('0.08'), contact_email='', shipping_address_line1='', shipping_city='', shipping_country='', shipping_zip='')

    return print(cartSerializer.data)