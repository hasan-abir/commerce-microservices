from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from checkout_api.serializers import CartSerializer, CartItemSerializer, ProductSerializer
from checkout_api.models import Cart, Product, CartItem
from django.urls import get_resolver

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
        queryset = Cart.objects.get(pk=pk)

        serializer = CartSerializer(queryset, context={'request': request})

        return Response(serializer.data, status=200)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer