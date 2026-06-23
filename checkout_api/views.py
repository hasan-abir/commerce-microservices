from rest_framework import status, generics
from rest_framework.response import Response
from checkout_api.serializers import OrderItemSerializer, ProductSerializer, StripeWebhookSerializer, PlaceOrderSerializer, demo_products
from checkout_api.models import Order
import redis
import stripe
import os
import json
from django.conf import settings
import logging
from checkout_api.tasks import sendreciept_task
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)
rd_instance = redis.Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)

stripe_api_key = os.environ.get('STRIPE_SECRET_KEY') or ''
stripe.api_key = stripe_api_key
stripe_webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET') or ''
stripe_client = stripe.StripeClient(stripe_api_key)

class ClientHomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_publishable_key"] = os.environ.get('STRIPE_PUBLISHABLE_KEY')
        return context

class ClientPaymentView(TemplateView):
    template_name = 'payment.html'

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def list(self, request):
        return Response(demo_products, status=status.HTTP_200_OK)

class PlaceOrderView(generics.CreateAPIView):
    serializer_class = PlaceOrderSerializer

    def create(self, request):
        body = request.data

        # validate input
        placed_order = PlaceOrderSerializer(data=body)

        if not placed_order.is_valid():
            return Response(placed_order.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # prepare for payment intent
        totals = calculate_totals(placed_order.validated_data['cart_items'])

        if isinstance(totals, dict):
            totals_err = totals
            return Response(totals_err, status=status.HTTP_400_BAD_REQUEST)
        
        try:    
            intent = stripe.PaymentIntent.create(
                amount=totals,
                currency='usd',
                automatic_payment_methods={
                    'enabled': True,
                },
            )
        except stripe.error.AuthenticationError as e:
            return Response({'stripe': 'API Key not provided'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.InvalidRequestError as e:
            body = e.json_body

            return Response({'stripe': body['error']['message']}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create order in DB
        order = Order.objects.create(contact_email=placed_order.validated_data['order']['contact_email'], total=totals, payment_intent_id=intent['id'])

        # Convert cart items into order items for DB
        order_items = create_orderitems_from_cart(order, placed_order.validated_data['cart_items'])

        if isinstance(order_items, dict):
            orderitems_err = order_items
            return Response(orderitems_err, status=status.HTTP_400_BAD_REQUEST)

        return Response({'clientSecret': intent['client_secret'], 'totals': totals, 'msg': "Order drafted! Now complete the payment to confirm it.", 'status': status.HTTP_200_OK})
    
class StripeWebhookView(generics.CreateAPIView):
    # serializer_class = StripeWebhookSerializer

    def create(self, request):
        # Frontend will provide it
        payload = request.body
        event = None

        # validate payment made
        try:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe_api_key
            )
        except ValueError as e:
            return Response({'msg': 'Error loading the payment event!'}, status=status.HTTP_400_BAD_REQUEST)

        if stripe_webhook_secret:
            sig_header = request.headers.get('stripe-signature')
            try:
                event = stripe_client.construct_event(
                    payload, sig_header, stripe_webhook_secret
                )
            except stripe.error.SignatureVerificationError as e:
                print('⚠️  Webhook signature verification failed.' + str(e))
                return Response({'success': False}, status=status.HTTP_401_UNAUTHORIZED)

        # validate payment status
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object

            order = Order.objects.get(payment_intent_id=payment_intent['id'])

            order.status = Order.PAID

            order.save()

            sendreciept_task.delay(order.pk)

            return Response({'msg': "Order paid successfully!", 'status': status.HTTP_200_OK})
        elif event.type == 'payment_intent.payment_failed':
            payment_intent = event.data.object

            order = Order.objects.get(payment_intent_id=payment_intent['id'])

            order.status = Order.CANCELLED

            order.save()

            sendreciept_task.delay(order.pk)
            
            return Response({'msg': 'Order failed and cancelled!'}, status=status.
            HTTP_400_BAD_REQUEST) 
        else:
            return Response({'msg': f'Unhandled event type {event.type}'}, status=status.HTTP_400_BAD_REQUEST)

def calculate_totals(cart_items):
    totals = 0

    for index, cart_item in enumerate(cart_items):
        validated_data = cart_item

        matched_product = next((product for product in demo_products if product.get('id') == validated_data['product_id']), None)
        
        totals += matched_product['price_cents'] * validated_data['product_quantity']

    if totals < 50:
        return {'cart_items': 'Cart cannot be empty!'}
    
    return totals

def create_orderitems_from_cart(order, cart_items):
    for index, cart_item in enumerate(cart_items):
        validated_data = cart_item

        data = {
            'item_id': validated_data['product_id'],
            'quantity': validated_data['product_quantity'],
            'price': validated_data['product_price'],
            'title': validated_data['product_title'],
            'order': order.pk
        }

        order_item = OrderItemSerializer(data=data)

        if not order_item.is_valid():
            return {f'msg_item_{index + 1}': order_item.errors}
        
        order_item.save()
    
    return None
