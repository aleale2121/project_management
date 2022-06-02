from core.models import Chat, Message
from rest_framework import serializers


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ["id","name","friends"]
        depth=1

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id","user","chat","content","created_at"]
        depth=1