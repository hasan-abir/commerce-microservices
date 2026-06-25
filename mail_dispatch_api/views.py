from rest_framework.views import APIView
from rest_framework.response import Response
from mail_dispatch_api.serializers import EmailDataSerializer
from mail_dispatch_api.tasks import sendmail_task
from rest_framework import status, generics

class DispatchAPIView(generics.CreateAPIView):
    serializer_class = EmailDataSerializer

    def create(self, request):
        serializer = EmailDataSerializer(data=request.data)
        if serializer.is_valid():
            serialized_data = serializer.validated_data
            sendmail_task.delay(serialized_data)
            return Response({'msg': "Success! We've accepted your email request and are dispatching the message now."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
