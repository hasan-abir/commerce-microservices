from django.shortcuts import render
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, mixins, views, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from checkout_api.serializers import OrderSerializer, OrderDataSerializer, demo_products
from checkout_api.models import Order
from checkout_api.serializers import CartItemSerializer, OrderDataSerializer
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, inline_serializer
import redis
import json
import stripe
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
rd_instance = redis.Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY') or ''

class ProductListView(views.APIView):
    def get(self, request, format=None):
        return Response(demo_products, status=status.HTTP_200_OK)

class PlaceOrderView(views.APIView):
    def post(self, request, format=None):
        # Validate user input with a hardcoded product list and serializer
        body = request.data
        order = body.get('order')
        cart_items = body.get('cart_items')

        if not order:
            return Response({'msg': 'Key "order" is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if not isinstance(cart_items, list) or len(cart_items) == 0:
            return Response({'msg': 'Key "cart_items" is required and it must be a list'}, status=status.HTTP_400_BAD_REQUEST)
        
        for index, item in enumerate(cart_items):
            item_data = CartItemSerializer(data=item)

            if not item_data.is_valid():
                return Response({f'msg_item_{index + 1}': item_data.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        order_data = OrderDataSerializer(data=order)
            
        if not order_data.is_valid():
                return Response({'msg': order_data.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Evaluate totals and create Order based on it

        # Create payment intent and return response token

        return Response({'msg': "Order drafted! Now complete the payment to confirm it.", 'status': status.HTTP_200_OK})
    
class StripeWebhookView(views.APIView):
    def post(self, request, format=None):
        return Response({'msg': "Order confirmed! Wait at the front door for 4 months.", 'status': status.HTTP_200_OK})

