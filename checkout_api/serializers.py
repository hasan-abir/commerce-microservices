from rest_framework import serializers, validators
from checkout_api.models import Product, Cart, CartItem
from decimal import *

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=round(Decimal(0.01), 2))
    stock = serializers.IntegerField(min_value=1)
    class Meta:
        model = Product
        fields = ['url', 'id', 'name', 'price', 'stock', 'is_active']

class CartSerializer(serializers.HyperlinkedModelSerializer):
    session_key = serializers.CharField(validators=[validators.UniqueValidator(queryset=Cart.objects.all(), message="Cart with this session key already exists.")])
    class Meta:
        model = Cart
        fields = ['url', 'id', 'session_key']

class CartItemSerializer(serializers.HyperlinkedModelSerializer):
    quantity = serializers.IntegerField(min_value=1)
    class Meta:
        model = CartItem
        fields = ['url', 'id', 'cart', 'product', 'quantity']