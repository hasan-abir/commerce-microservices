from rest_framework import serializers
from checkout_api.models import Order, OrderItem
from decimal import *

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderDataSerializer(serializers.Serializer):
    contact_email = serializers.EmailField()

class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_quantity = serializers.IntegerField()

    def validate(self, attrs):
        product = next((item for item in demo_products if item['id'] == attrs['product_id']), None)

        if product:
            if attrs['product_quantity'] <= product['stock']:
                return attrs
            else:
                raise serializers.ValidationError({'product_quantity': 'Quantity exceeds the product.'})
        else:
            raise serializers.ValidationError({'product_id': f"Product with id {attrs['product_id']} doesn't exist."})         
        
demo_products = [
    {"id": 1, "title": "Abstract Horizon Painting", "price_cents": 5500, "stock": 5},
    {"id": 2, "title": "Minimalist Ceramic Vase", "price_cents": 3200, "stock": 12},
    {"id": 3, "title": "Handwoven Cotton Throw", "price_cents": 4500, "stock": 8},
    {"id": 4, "title": "Solid Oak Nightstand", "price_cents": 12000, "stock": 3},
    {"id": 5, "title": "Artisanal Scented Candle", "price_cents": 1800, "stock": 25},
    {"id": 6, "title": "Industrial Desk Lamp", "price_cents": 6500, "stock": 10},
    {"id": 7, "title": "Velvet Accent Pillow", "price_cents": 2500, "stock": 15},
    {"id": 8, "title": "Matte Black Pour-Over Kit", "price_cents": 4200, "stock": 7},
    {"id": 9, "title": "Geometric Wall Mirror", "price_cents": 8500, "stock": 4},
    {"id": 10, "title": "Recycled Glass Carafe", "price_cents": 2800, "stock": 20}
]