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
from mail_dispatch_api.tasks import sendmail_task

logger = logging.getLogger(__name__)
rd_instance = redis.Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY') or ''

class ProductListView(views.APIView):
    def get(self, request, format=None):
        return Response(demo_products, status=status.HTTP_200_OK)

class PlaceOrderView(views.APIView):
    def post(self, request, format=None):
        body = request.data
        order = body.get('order')
        cart_items = body.get('cart_items')

        if not order:
            return Response({'msg': "Key 'order' is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if not isinstance(cart_items, list) or len(cart_items) == 0:
            return Response({'msg': "Key 'cart_items' is required and it must be a list"}, status=status.HTTP_400_BAD_REQUEST)
        
        totals = calculate_totals(cart_items)

        if isinstance(totals, dict):
            totals_err = totals
            return Response(totals_err, status=status.HTTP_400_BAD_REQUEST)
            
        order_data = OrderDataSerializer(data=order)
            
        if not order_data.is_valid():
                return Response({'msg': order_data.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        intent = stripe.PaymentIntent.create(
            amount=totals,
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
            },
        )

        Order.objects.create(contact_email=order_data['contact_email'].value, total=totals, payment_intent_id=intent['id'])

        return Response({'clientSecret': intent['client_secret'], 'totals': totals, 'msg': "Order drafted! Now complete the payment to confirm it.", 'status': status.HTTP_200_OK})
    
class StripeWebhookView(views.APIView):
    def post(self, request, format=None):
        # Frontend will provide it
        payload = request.data
        event = None

        try:
            event = stripe.Event.construct_from(
            payload, stripe.api_key
            )
        except ValueError as e:
            return Response({'msg': 'Error loading the payment event!'}, status=status.HTTP_400_BAD_REQUEST)

        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object

            order = Order.objects.get(payment_intent_id=payment_intent['id'])

            order.status = Order.PAID

            order.save()

            # send recipet in mail

            return Response({'msg': "Order paid successfully!", 'status': status.HTTP_200_OK})
        elif event.type == 'payment_intent.payment_failed':
            payment_intent = event.data.object

            order = Order.objects.get(payment_intent_id=payment_intent['id'])

            order.status = Order.CANCELLED

            order.save()

            # send recipet in mail
            
            return Response({'msg': 'Order failed and cancelled!'}, status=status.
            HTTP_400_BAD_REQUEST) 
        else:
            return Response({'msg': f'Unhandled event type {event.type}'}, status=status.HTTP_400_BAD_REQUEST)

        


def calculate_totals(cart_items):
    totals = 0

    for index, cart_item in enumerate(cart_items):
        cart_item_data = CartItemSerializer(data=cart_item)


        if not cart_item_data.is_valid():
            return {f'msg_item_{index + 1}': cart_item_data.errors}
        
        validated_data = cart_item_data.validated_data

        matched_product = next((product for product in demo_products if product.get('id') == validated_data['product_id']), None)
        
        totals += matched_product['price_cents'] * validated_data['product_quantity']

    return totals