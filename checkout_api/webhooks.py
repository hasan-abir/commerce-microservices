from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework import views

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(views.APIView):
    def post(self, request, *args, **kwargs):
        return Response({"msg": "Order confirmed!"}, status=200)
