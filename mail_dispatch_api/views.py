from rest_framework.views import APIView
from rest_framework.response import Response
from mail_dispatch_api.serializers import EmailDataSerializer
from mail_dispatch_api.tasks import sendmail_task

class DispatchAPIView(APIView):
    def post(self, request, format=None):
        serializer = EmailDataSerializer(data=request.data)
        if serializer.is_valid():
            serialized_data = serializer.validated_data
            sendmail_task.delay(serialized_data)
            return Response({'msg': "Success! We've accepted your email request and are dispatching the message now."})
        else:
            return Response(serializer.errors, status=400)
