from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Chat, Contact
from rest_framework.response import Response


User = get_user_model()
class ContactSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class ChatSerializer(serializers.ModelSerializer):
    participants = ContactSerializer(many=True)
    class Meta:
        model = Chat
        fields = ('id', 'messages', 'participants')
        read_only = ('id')

    def create(self, validated_data):
        print(validated_data)
        participants = validated_data.pop('participants')
        chat = Chat()
        chat.save()
        for username in participants:
            contact = None
            try:
                user = User.objects.get(username=username)
                contact=Contact.objects.get(user=user)
            except:
                return Response({"error":"User not Found!"}, content_type="application/json")
            chat.participants.add(contact)
        chat.save()
        return chat