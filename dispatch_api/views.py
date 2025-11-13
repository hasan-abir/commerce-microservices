from rest_framework.views import APIView
from rest_framework.response import Response
from dispatch_api.serializers import EmailDataSerializer

class DispatchAPIView(APIView):
    def post(self, request, format=None):
        serializer = EmailDataSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        else:
            return Response(serializer.errors, status=400)
