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

class PlaceOrderView(views.APIView):
    def post(self, request, format=None):
        # Validate user input with a hardcoded product list and serializer

        # Evaluate totals and create Order based on it

        # Create payment intent and return response token

        return Response({'msg': "Order drafted! Now complete the payment to confirm it.", 'status': status.HTTP_200_OK})
    
class StripeWebhookView(views.APIView):
    def post(self, request, format=None):
        return Response({'msg': "Order confirmed! Wait at the front door for 4 months.", 'status': status.HTTP_200_OK})
