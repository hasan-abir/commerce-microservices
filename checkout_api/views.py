from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from checkout_api.serializers import CartSerializer, CartItemSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer
from checkout_api.models import Cart, Product, CartItem, Order, OrderItem
from checkout_api.tasks import placeorder_task

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

class OrderViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        queryset = Order.objects.all()

        order = get_object_or_404(queryset, pk=pk)

        serializer = OrderSerializer(order, context={'request': request})

        return Response(serializer.data, status=200)
    
    def create(self, request):
        data = { 'session_key': request.session.session_key }

        if not data['session_key']:
            return Response({'msg': 'Create your cart first.'}, status=400)

        cartItems = CartItem.objects.filter(cart__session_key=data['session_key'])

        if len(cartItems) < 1:
            return Response({'msg': 'Add items to your cart first.'}, status=400)

        placeorder_task.delay(data)
        return Response({'msg': "Success! We've accepted your order request and are dispatching the products now."}, status=200)

        
class OrderItemViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        queryset = OrderItem.objects.all()

        order_item = get_object_or_404(queryset, pk=pk)

        serializer = OrderItemSerializer(order_item, context={'request': request})

        return Response(serializer.data, status=200)