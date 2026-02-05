from django.shortcuts import render
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, mixins, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from checkout_api.serializers import CartSerializer, CartItemSerializer, CartItemRequestSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, OrderDataSerializer, PaymentSerializer, PaymentIntentSerializer
from checkout_api.models import Cart, Product, CartItem, Order, OrderItem, PaymentIntent
from checkout_api.tasks import placeorder_task
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, inline_serializer, extend_schema_view
from django.urls import reverse
import redis
import json
import stripe
import os
import logging

logger = logging.getLogger(__name__)
rd_instance = redis.Redis(host='redis', port=6379, decode_responses=True)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY') or ''

class ProductViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,viewsets.GenericViewSet):
    serializer_class = ProductSerializer

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
class CartViewSet(viewsets.ViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def list(self, request):
        if not request.session.session_key:
            request.session.save()
        
        session_key = request.session.session_key

        cart = Cart.objects.filter(session_key=session_key, status=Cart.ACTIVE).first()

        if not cart:
            request.session.cycle_key()
            new_session_key = request.session.session_key

            cart = Cart.objects.create(session_key=new_session_key)

        serializer = CartSerializer(cart, context={'request': request})

        return Response(serializer.data, status=200)
    
    def retrieve(self, request, pk: int):
        cart_item = get_object_or_404(self.queryset, pk=pk)

        serializer = CartSerializer(cart_item, context={'request': request})

        return Response(serializer.data, status=200)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    @extend_schema(
        request=CartItemRequestSerializer, 
        responses={201: CartItemSerializer},
        methods=['POST']
    )
    def create(self, request, *args, **kwargs):
        try:
            session_key = checkSessionKey(request)

            if not isinstance(session_key, str):
                return Response(session_key['body'], status=session_key['status'])
            
            idemotencyError = checkIdempotency(request, session_key, expiration=30)

            if idemotencyError:
                return Response(idemotencyError['body'], status=idemotencyError['status'])
            
            cart = Cart.objects.get(session_key=session_key)

            cart_url = reverse('cart-detail', kwargs={'pk': cart.pk})

            data = request.data.copy()

            data['cart'] = cart_url 

            serializer = self.get_serializer(data=data)

            serializer.is_valid(raise_exception=True)

            with transaction.atomic(): 
                product_id = int(request.data['product'].split('/products')[-1].strip("/"))

                error = checkOutofStock(session_key, product_id, int(request.data['quantity']))

                if error is not None:
                    return Response(error['body'], status=error['status'])
            
            self.perform_create(serializer)
            return Response(serializer.data, status=201)
        except Exception as e:
            # exc_info is to trace the error
            logger.error(f"Order failed for session {session_key}: {e}", exc_info=True)
            raise e
    
    @extend_schema(
        request=CartItemRequestSerializer, 
        responses={200: CartItemSerializer},
        methods=['PUT']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        request=CartItemRequestSerializer, 
        responses={200: CartItemSerializer},
        methods=['PATCH']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        session_key = checkSessionKey(self.request)

        if not isinstance(session_key, str):
            raise ValidationError({'msg': session_key['body']['msg']})
        
        cart = get_object_or_404(Cart, session_key=session_key)

        serializer.save(cart=cart)


class OrderViewSet(viewsets.ViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def retrieve(self, request, pk):
        order = get_object_or_404(self.queryset, pk=pk)

        serializer = OrderSerializer(order, context={'request': request})

        return Response(serializer.data, status=200)
    
    @extend_schema(
        request=OrderDataSerializer, 
        responses={200: inline_serializer(
            name='OrderResponse',
            fields={
                'msg': serializers.CharField()
            })},
        methods=['POST']
    )
    def create(self, request):

        session_key = checkSessionKey(request)

        if not isinstance(session_key, str):
            return Response(session_key['body'], session_key['status'])
        
        idemotencyError = checkIdempotency(request, session_key, expiration=3600)

        if idemotencyError:
            return Response(idemotencyError['body'], status=idemotencyError['status'])

        cartItems = CartItem.objects.filter(cart__session_key=session_key)

        if len(cartItems) < 1:
            return Response({'msg': 'Add items to your cart first.'}, status=400)
                    
        data = request.data.copy()
        serializer = OrderDataSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        try:
            with transaction.atomic(): 
                for item in cartItems:
                    error = checkOutofStock(session_key, item.product.id, item.quantity, True)

                    if error is not None:
                        if error['status'] == 400:
                            item.delete()

                        return Response(error['body'], status=error['status'])
            
            data['session_key'] = session_key

            placeorder_task.delay(data)
            
            return Response({'msg': "Success! We've accepted your order request and are dispatching the products now."}, status=200)
        except Exception as e:
            # exc_info is to trace the error
            logger.error(f"Order failed for session {session_key}: {e}", exc_info=True)
            raise e
        
class OrderItemViewSet(viewsets.ViewSet):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()

    def retrieve(self, request, pk):
        order_item = get_object_or_404(self.queryset, pk=pk)

        serializer = OrderItemSerializer(order_item, context={'request': request})

        return Response(serializer.data, status=200)
    
class PaymentViewSet(viewsets.ViewSet):
    def create(self, request):
        try:
            if not request.session.session_key:
                request.session.save()

            session_key = request.session.session_key

            idemotencyError = checkIdempotency(request, session_key, 3600)

            if idemotencyError:
                return Response(idemotencyError['body'], status=idemotencyError['status'])

            payment_serializer = PaymentSerializer(data=request.data)

            if not payment_serializer.is_valid():
                return Response(payment_serializer.errors, status=400)
            
            totals = request.data['total']
            intent = stripe.PaymentIntent.create(
                amount=totals,
                currency='usd',
            )

            data = {
                'amount': totals,
                'currency': 'usd',
                'order_id': request.session.session_key,
                'payment_intent_id': intent['id'],
                'payment_method_id': intent['payment_method']
            }

            payment_intent_serializer = PaymentIntentSerializer(data=data)

            if not payment_intent_serializer.is_valid():
                return Response(payment_intent_serializer.errors, status=400)
            payment_intent_serializer.save()

            return Response({
                'clientSecret': intent['client_secret'],
            }, status=200)
        except Exception as e:
             return Response({'msg': str(e)}, status=403)

# CHECK DB ON HOW TO CONFIRM PAYMENT INTENTS. MAIN TASK HERE IS TO CHANGE STATUS OF PAYMENT INTENT
class PaymentConfirmView(views.APIView):
    def post(self, request, *args, **kwargs):
        idemotencyError = checkIdempotency(request)

        if idemotencyError:
            return Response(idemotencyError['body'], status=idemotencyError['status'])

        payment_intent_id = request.data.get('payment_intent_id')

        payment_intent_instance = get_object_or_404(PaymentIntent, payment_intent_id=payment_intent_id)

        try:
            stripe_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if stripe_intent.status == 'succeeded':
                payment_intent_instance.status = PaymentIntent.SUCCEEDED
                payment_intent_instance.save()
                return Response({'msg': 'Payment verified and succeeded!'}, status=200)
            
            else:
                payment_intent_instance.status = PaymentIntent.FAILED
                payment_intent_instance.save()
                return Response({'msg': f'Stripe says: {stripe_intent.status}'}, status=400)

        except stripe.error.StripeError as e:
            return Response({'error': 'Stripe communication error'}, status=500)         
    
def checkOutofStock(session_key, product_id, quantity, mutate_cart = False):
    product = Product.objects.select_for_update().filter(id=product_id).first()

    if product is None:
        return {
            'body': {
                'msg': 'Product not found.',
            },
            'status': 404
        }


    if product.stock >= quantity:
        if mutate_cart:
        # F() is to get the value straight from DB and not store it in Python's memory
            product.stock = F('stock') - quantity
            product.save()
            
            cart = Cart.objects.get(session_key=session_key)
            cart.status = Cart.PROCESSING
            cart.save()

        return None
    else:
        return {
            'body': {
                'msg': f'{product.name}: Out of stock',
            },
            'status': 400
        }
    
def checkSessionKey (request):
    session_key = request.session.session_key

    if session_key:
        return session_key;
    else:
        return {
            'body': {
                'msg': 'Create your cart first.',
            },
            'status': 400
        }
    
def checkIdempotency(request, session_key = 'unset', expiration = 30):
    if not 'Idempotency-Key' in request.headers:
        return {
            "body": {'msg': "Specify a 'Idempotency-Key' attribute in the headers with a UUID"},
            "status": 400
        }
    
    idem_key = request.headers.get('Idempotency-Key')

    payload = json.dumps({'session_key': session_key, 'body': str(request.body)})
    success = rd_instance.set(idem_key, payload, nx=True, ex=expiration)

    if not success:
        return {"body": {'msg': "Duplicate request detected"}, "status": 409}
    
    return None;