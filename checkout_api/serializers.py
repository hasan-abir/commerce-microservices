from rest_framework import serializers, validators
from checkout_api.models import Product, Cart, CartItem
from decimal import *

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=round(Decimal(0.01), 2))
    stock = serializers.IntegerField(min_value=1)
    class Meta:
        model = Product
        fields = ['url', 'id', 'name', 'price', 'stock', 'is_active']

class CartSerializer(serializers.ModelSerializer):
    session_key = serializers.CharField(validators=[validators.UniqueValidator(queryset=Cart.objects.all(), message="Cart with this session key already exists.")])
    total = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['url', 'id', 'session_key', 'total', 'subtotal']

    def get_subtotal(self, obj):
        cart_subtotal = 0

        cartItems = CartItem.objects.filter(cart=obj)

        for cartItem in cartItems:
            cart_subtotal += cartItem.product.price * cartItem.quantity

        cart_subtotal = Decimal(cart_subtotal)

        return cart_subtotal.quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    
    def get_total(self, obj):
        tax_rate = Decimal("0.08")
        cart_subtotal = self.get_subtotal(obj)

        cart_total = cart_subtotal + cart_subtotal * tax_rate

        cart_total = Decimal(cart_total)

        return cart_total.quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    

class CartItemSerializer(serializers.HyperlinkedModelSerializer):
    quantity = serializers.IntegerField(min_value=1)
    class Meta:
        model = CartItem
        fields = ['url', 'id', 'cart', 'product', 'quantity']