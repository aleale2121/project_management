import json
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView
)
from core.models import Batch, Chat, Contact, Student,User
from chat.views import get_last_40_messages, get_user_contact
from rest_framework.decorators import action
from .serializers import ChatSerializer
from rest_framework.viewsets import ModelViewSet
from constants.constants import MODEL_ALREADY_EXIST, MODEL_DELETE_FAILED, MODEL_RECORD_NOT_FOUND
from pkg.util import error_response, success_response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response


class ChatListView(ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = (permissions.AllowAny, )

    def get_queryset(self):
        print("query set  ...")
        queryset = Chat.objects.all()
        username = self.request.query_params.get('username')
        print("username ",username)
        if username is not None:
            contact=get_user_contact(username)
            print("c  ",contact)
            if contact is None:
                print("line 36")
                return []
                
            queryset=contact.chats.all()
            print("q=",queryset)
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
    
    
    @action(
        detail=True,
        methods=['GET'],
        url_path='messages',
    )
    def get_user_chat_message(self, request, *args, **kwargs):
        chat_messages=None
        chatId=0
        id=kwargs['pk']
        print("pk=> ",id)
        contact=None
        if id:
            chatId=int(id)
        print("line 81")
        chat_messages=get_last_40_messages(chatId)
        data=ChatSerializer(chat_messages).data
        return Response(data)

    
    @action(
        detail=False,
        methods=['POST'],
        url_path='new',
    )
    def create_new_chat(self, request):
        print("creating ...")
        id = int(request.user.id)
        print("user id ",id)
        data=request.data
        user_obj=None
        contact_obj=None
        if not User.objects.filter(username=self.request.user.username,is_staff=True).exists():
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Chat")
            res['message']="You don't have enough permission to create new chat room!"
            return Response(res, status=res['status_code'],content_type="application/json")
        if id:
            try:
              user_obj=User.objects.get(id=id)
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "Chat")
                res["message"]="User seems anonymous."
                return Response(res,status=res['status_code'], content_type="application/json")
                        
        try:
            print("user obj",user_obj)
            if Contact.objects.filter(user=user_obj).exists():
                contact_obj=Contact.objects.filter(user=user_obj)[0]
                contact_obj.admin=True
                contact_obj.save()
                
            else:
                contact_obj=Contact.objects.create(user=user_obj,admin=True)
                
        except:
            print("contact_obj =>",contact_obj)
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Contact")
            res["message"]="No contact user found!."
            return Response(res, status=res['status_code'],content_type="application/json")
                 
        chat_obj=Chat(name=data["name"])
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
        user_obj=None
        contact_obj=None
        chat_obj=None
        print("data ===",form_data)
        user=None
        try:
            user = User.objects.get(username=self.request.user.username)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
            res['message']=f"No user record found with username {username} to add new member."
            return Response(res, status=res['status_code'],content_type="application/json")
        
        if not User.objects.filter(username=self.request.user.username,is_staff=True).exists() and not Contact.objects.filter(user=user,admin=True).exists():
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Chat")
            res['message']="You don't have enough permission to add new member!"
            return Response(res, status=res['status_code'],content_type="application/json")
        try:
            user_obj = User.objects.get(username=username)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
            res['message']=f"No user record found with username {username}."
            return Response(res, status=res['status_code'],content_type="application/json")
      
        try:
            if Contact.objects.filter(user=user_obj).exists():
                contact_obj=Contact.objects.filter(user=user_obj)[0]
            else:
                contact_obj=Contact.objects.create(user=user_obj)       
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Contact")
            res['message']='No user contact found.'
            return Response(res, status=res['status_code'],content_type="application/json")
        try:
            chat_obj = Chat.objects.get(id=chatId)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Chat")
            res['message']=f'No chat found with id {chatId}'
            return Response(res, content_type="application/json",status=res['status_code'])
        chat_obj.participants.add(contact_obj)
        serializer=ChatSerializer(chat_obj)
        return Response(serializer.data)
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
        if not User.objects.filter(username=self.request.user.username,is_staff=True).exists() and not Contact.objects.filter(user=user,admin=True).exists():
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Chat")
            res['message']="You don't have enough permission to remove member from chat room!"
            return Response(res, status=res['status_code'],content_type="application/json")
        try:
            user_obj = User.objects.get(username=username)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
            res['message']=f"No user record found with username {username}."
            return Response(res,status=res['status_code'],content_type="application/json")
        try:
            contact_obj = Contact.objects.filter(user=user_obj)[0]
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Contact")
            res['message']='No user contact found.'
            return Response(res,status=res['status_code'],content_type="application/json")
        try:
            chat_obj = Chat.objects.get(id=chatId)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Chat")
            res['message']=f'No chat found with id {chatId}'
            return Response(res,status=res['status_code'],content_type="application/json")
        chat_obj.participants.remove(contact_obj)
        print("line --- 211")
        return Response({"message":"Member Succesfully removed from the  channels"})
    def destroy(self, request, *args, **kwargs):
        print("deleting...")
        if not User.objects.filter(username=self.request.user.username,is_staff=True).exists() and not Contact.objects.filter(user=user,admin=True).exists():
            res = error_response(request, MODEL_DELETE_FAILED, "Chat")
            res['message']="You don't have enough permission to delete chat room!"
            return Response(res, status=res['status_code'],content_type="application/json")
        instance = Chat.objects.filter(id=str(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "Chat")
            return Response(res, status=int(res['status_code']),content_type="application/json")
        instance.delete()
        return Response({"result": "Semister instance was successfuly deleted!"})

        
        
        
        




