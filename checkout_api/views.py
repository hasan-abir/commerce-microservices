from django.shortcuts import render
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, mixins, views, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from checkout_api.serializers import OrderSerializer, OrderDataSerializer
from checkout_api.models import Order
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

        # Evaluate totals and create Order based on it

        # Create payment intent and return response token

        return Response({'msg': "Order drafted! Now complete the payment to confirm it.", 'status': status.HTTP_200_OK})
    
class StripeWebhookView(views.APIView):
    def post(self, request, format=None):
        return Response({'msg': "Order confirmed! Wait at the front door for 4 months.", 'status': status.HTTP_200_OK})

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