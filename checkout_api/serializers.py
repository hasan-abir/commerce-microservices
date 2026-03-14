from rest_framework import serializers
from checkout_api.models import Order
from decimal import *

class OrderSerializer(serializers.HyperlinkedModelSerializer):
    order_number = serializers.CharField(read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=3, min_value=Decimal('0.01'))
    class Meta:
        model = Order
        fields = '__all__'

class OrderDataSerializer(serializers.Serializer):
    contact_email = serializers.EmailField()
    shipping_address_line1 = serializers.CharField(max_length=100)
    shipping_zip = serializers.CharField(max_length=100)
    shipping_city = serializers.CharField(max_length=100)
    shipping_country = serializers.CharField(max_length=100)

