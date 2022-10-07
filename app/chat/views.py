from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from core.models import Chat, Contact

User = get_user_model()


def get_last_40_messages(chatId):
    chat=None
    try:
        chat = Chat.objects.get(id=chatId)
    except:
        return None 
    return chat.messages.all().order_by('-timestamp')[:5]

def get_user_contact(username):
    user=None
    contact=None
    try:
        user = User.objects.get(username=username)
    except:
        return None
    try:
        contact = Contact.objects.get( user=user)
    except:
        return None 
    return contact


def get_current_chat(chatId):
    chat=None
    try:
        print("chat ID",chatId)
        chat = Chat.objects.get(id=chatId)
    except:
        print("line 36")
        return
    return chat