from rest_framework import serializers

class EmailDataSerializer(serializers.Serializer):
    recipient = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    msg_content = serializers.CharField()