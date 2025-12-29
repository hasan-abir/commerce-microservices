from django.shortcuts import render
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from checkout_api.serializers import CartSerializer, CartItemSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, OrderDataSerializer
from checkout_api.models import Cart, Product, CartItem, Order, OrderItem
from checkout_api.tasks import placeorder_task
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class ProductViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        queryset = Product.objects.all()

        product = get_object_or_404(queryset, pk=pk)

        serializer = ProductSerializer(product, context={'request': request})

        return Response(serializer.data, status=200)
    
class CartViewSet(viewsets.ViewSet):
    def list(self, request):
        if not request.session.session_key:
            request.session.save()
        
        session_key = request.session.session_key

        cart, created = Cart.objects.get_or_create(session_key=session_key)

        serializer = CartSerializer(cart, context={'request': request})

        return Response(serializer.data, status=200)
    
    def retrieve(self, request, pk):
        queryset = Cart.objects.all()
        cart_item = get_object_or_404(queryset, pk=pk)

        serializer = CartSerializer(cart_item, context={'request': request})

        return Response(serializer.data, status=200)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def perform_create(self, serializer):
        session_key = self.request.session.session_key

        if not session_key:
            raise ValidationError({'msg': 'Create your cart first'})

        cart = get_object_or_404(Cart, session_key=session_key)

        serializer.save(cart=cart)


class OrderViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        queryset = Order.objects.all()

        order = get_object_or_404(queryset, pk=pk)

        serializer = OrderSerializer(order, context={'request': request})

        return Response(serializer.data, status=200)
     
    def create(self, request):
        session_key = request.session.session_key

        if not session_key:
            return Response({'msg': 'Create your cart first.'}, status=400)

        cartItems = CartItem.objects.filter(cart__session_key=session_key)

        if len(cartItems) < 1:
            return Response({'msg': 'Add items to your cart first.'}, status=400)
        
        data = request.data.copy()
        serializer = OrderDataSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, 400)
        
        try:
            with transaction.atomic(): 
                for item in cartItems:
                    # Will allow rolling back db changes if the service crashes
                        product = Product.objects.select_for_update().get(id=item.product.id)

                        if product.stock >= item.quantity:
                            # F() is to get the value straight from DB and not store it in Python's memory
                            product.stock = F('stock') - item.quantity
                            product.save()
                            
                            data['session_key'] = session_key

                            placeorder_task.delay(data)
                        else:
                            return Response({'msg': 'Out of stock'}, status=400)
            
            return Response({'msg': "Success! We've accepted your order request and are dispatching the products now."}, status=200)
        except Exception as e:
            # exc_info is to trace the error
            logger.error(f"Order failed for session {session_key}: {e}", exc_info=True)
            raise e
        
class OrderItemViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        queryset = OrderItem.objects.all()

        order_item = get_object_or_404(queryset, pk=pk)

        serializer = OrderItemSerializer(order_item, context={'request': request})

        return Response(serializer.data, status=200)