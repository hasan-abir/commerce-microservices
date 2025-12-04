from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from checkout_api.serializers import CartSerializer
from checkout_api.models import Cart
from django.urls import get_resolver

class CartViewSet(ViewSet):
    def list(self, request):
        if not request.session.session_key:
            request.session.save()
        
        session_key = request.session.session_key

        cart, created = Cart.objects.get_or_create(session_key=session_key)

        serializer = CartSerializer(cart, context={'request': request})

        return Response(serializer.data)
