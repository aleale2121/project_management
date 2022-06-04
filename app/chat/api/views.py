from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView
)
from core.models import Batch, Chat, Contact, Student
from chat.views import get_user_contact
from rest_framework.decorators import action
from .serializers import ChatSerializer
from rest_framework.viewsets import ModelViewSet
from constants.constants import MODEL_ALREADY_EXIST, MODEL_RECORD_NOT_FOUND
from pkg.util import error_response, success_response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response



User = get_user_model()


class ChatListView(ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = (permissions.AllowAny, )

    def get_queryset(self):
        queryset = Chat.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            contact = get_user_contact(username)
            queryset = contact.chats.all()
        return queryset


class ChatDetailView(RetrieveAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.AllowAny, )


class ChatCreateView(CreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated, )


class ChatUpdateView(UpdateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated, )


class ChatDeleteView(DestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated, )
    
class ChatModelViewSet(ModelViewSet):
    serializer_class = ChatSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["id"]
    search_fields = ["id"]
    filter_fields = ["id"]

    def get_queryset(self):
        queryset = Chat.objects.all()
        return queryset
    @action(
        detail=False,
        methods=['POST'],
        url_path='new',
    )
    def create_new_chat(self, request):
        print("creating ...")
        id = int(request.user.id)
        print("user id ",id)
        user_obj=None
        contact_obj=None
        if id:
            try:
              user_obj=User.objects.get(id=id)
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "Chat")
                res["message"]="User seems anonymous."
                return Response(res, content_type="application/json")
                        
        try:
            print("user obj",user_obj)
            if Contact.objects.filter(user=user_obj).exists():
                contact_obj=Contact.objects.filter(user=user_obj).first()
            else:
                contact_obj=Contact.objects.create(user=user_obj)
        except:
            print("contact_obj =>",contact_obj)
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Contact")
            res["message"]="No contact user found!."
            return Response(res, content_type="application/json")
                 #######################################################
        chat_obj=Chat()
        chat_obj.save()
        chat_obj.participants.add(contact_obj)
        return Response({"message":"channel created successfully"})
    @action(
        detail=False,
        methods=['POST'],
        url_path='add',
    )
    def add_chat_member(self, request):
        form_data=request.data
        username=None
        chatId=0
        if form_data.get('username') and form_data.get('chatId'):
            username  =form_data['username']
            chatId    =form_data['chatId']
        batch_obj=None
        user_obj=None
        contact_obj=None
        chat_obj=None
        try:
            batch_obj = Batch.objects.get(is_active=True)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Batch")
            res['message']="No active batch found!"
            return Response(res, content_type="application/json")
        try:
            user_obj = User.objects.get(username=username)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
            res['message']=f"No user record found with username {username}."
            return Response(res, content_type="application/json")
        if Student.objects.filter(user=user_obj,batch=batch_obj).exists():
            pass
        else:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
            res['message']=f"No student record found with username {username}."
            return Response(res, content_type="application/json")
        try:
            if Contact.objects.filter(user=user_obj).exists():
                contact_obj=Contact.objects.filter(user=user_obj).first()
            else:
                contact_obj=Contact.objects.create(user=user_obj)       
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Contact")
            res['message']='No user contact found.'
            return Response(res, content_type="application/json")
        try:
            chat_obj = Chat.objects.get(id=chatId)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Chat")
            res['message']=f'No chat found with id {chatId}'
            return Response(res, content_type="application/json")
        chat_obj.participants.add(contact_obj)
        serializer=ChatSerializer(chat_obj)
        return Response({serializer.data})
    @action(
        detail=False,
        methods=['DELETE'],
        url_path="remove",
    )
    def remove_chat_member(self, request):
        print("removing ...")
        form_data=request.data
        username=None
        chatId=0
        if form_data.get('username') and form_data.get('chatId'):
            username  =form_data['username']
            chatId    =form_data['chatId']
        user_obj=None
        chat_obj=None
        contact_obj=None
        print(username,chatId)
        try:
            user_obj = User.objects.get(username=username)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
            res['message']=f"No user record found with username {username}."
            return Response(res, content_type="application/json")
        try:
            contact_obj = Contact.objects.filter(user=user_obj).first()
            print(len(contact_obj))
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Contact")
            res['message']='No user contact found.'
            return Response(res, content_type="application/json")
        try:
            chat_obj = Chat.objects.get(id=chatId)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Chat")
            res['message']=f'No chat found with id {chatId}'
            return Response(res, content_type="application/json")
        chat_obj.participants.remove(contact_obj)
        Response({"message":"Member Succesfully removed from the  channels"})
        




