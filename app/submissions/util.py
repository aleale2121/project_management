from urllib import response
from django.contrib.auth import get_user_model
from core.models import Chat, Contact
from rest_framework.response import Response


User = get_user_model()
def get_user_contact(username):
    contact = None
    try:
        user = User.objects.get(username=username)
        contact= Contact.objects.get(user=user)
        return contact
    except:
        return Response({"error":"User not Found!"}, content_type="application/json")


def get_current_chat(chatId):
    chat = None
    try:
        chat = Chat.objects.get(id=chatId)
        return chat
    except:
        return Response({"error":"Chat not Found!"}, content_type="application/json")
    
def get_last_10_messages(chatId):
    chat = get_current_chat(chatId)
    return chat.messages.order_by('-timestamp').all()[:10]
    
    
    