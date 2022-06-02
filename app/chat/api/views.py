from importlib.resources import contents
from constants.constants import MODEL_ALREADY_EXIST, MODEL_CREATION_FAILED, MODEL_DELETE_FAILED, MODEL_PARAM_MISSED, MODEL_RECORD_NOT_FOUND
from core.models import Chat,Message, Student,User
from django_filters.rest_framework import DjangoFilterBackend
from pkg.util import error_response, success_response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from .serializers import ChatSerializer, MessageSerializer

class ChatViewSet(ModelViewSet):
    serializer_class = ChatSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["name"]
    search_fields = ["name"]
    filter_fields = ["name"]
    def get_queryset(self):
        queryset = Chat.objects.all()
        return queryset
    def retrieve(self, request, pk=None):
        print("retriving ...")
        instance = None
        try:
            instance = Chat.objects.get(id=int(self.kwargs["pk"]))
        except:
            print("line 24")
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "Chat")
            return Response(res, content_type="application/json")   
        print("hello ")
        return Response(self.serializer_class(instance).data)
    
    def create(self, request, *args, **kwargs):
        print("chat creating  ...")
        data = request.data
        count=0 
        if  len(data)!=0:
            count= Chat.objects.filter(name=data["name"]).count()
        else:
            res = error_response(request, MODEL_CREATION_FAILED, "Chat")
            return Response(res, content_type="application/json")
        if count > 0:
            res = error_response(request, MODEL_ALREADY_EXIST, "Chat")
            return Response(res, content_type="application/json")
        chat_obj=None
        chat_obj = Chat.objects.create(name=data["name"])
        serializer = ChatSerializer(chat_obj)
        data = success_response(serializer.data)
        return Response((data))
    
    def update(self, request, *args, **kwargs):
        print("updating ...")
        data = request.data
        pk = kwargs["pk"]
        if pk:
            pk = int(pk)
        chat_obj =None
        try:
            chat_obj =  Chat.objects.get(pk=pk)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Chat")
            return Response(res, content_type="application/json")

        if data.get("name"):
            chat_obj.name = data["name"]
        else:
            pass
        
        chat_obj.save()
        print("updated.")
        serializer = ChatSerializer(chat_obj)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = Chat.objects.filter(id=(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "Chat")
            return Response(res, content_type="application/json")
        instance.delete()
        return Response({"result": "Chat instance was successfuly deleted!"})
 
 
 
 #Message viewsets
class MessageViewSet(ModelViewSet):
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["created_at"]
    search_fields = ["created_at"]
    filter_fields = ["created_at"]
    def get_queryset(self):
        queryset = Message.objects.all()
        return queryset
    def retrieve(self, request, pk=None):
        print("retriving ...")
        instance = None
        try:
            instance = Message.objects.get(id=int(self.kwargs["pk"]))
        except:
            print("line 24")
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "Chat")
            return Response(res, content_type="application/json")   
        return Response(self.serializer_class(instance).data)
    
    
    def create(self, request, *args, **kwargs):
        print("chat creating  ...")
        data = request.data
        chat_obj=None
        user_obj=None
        message_obj=None
        try:
            chat_obj = Chat.objects.get(id=data["chat"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Chat")
            return Response(res, content_type="application/json")
        
        try:
            user_obj = User.objects.get(id=data["user"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
            return Response(res, content_type="application/json")
        if not Student.objects.filter(user=data["user"]).exists():
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Student")
            return Response(res, content_type="application/json")
            
        if data.get("chat") and data.get("user"):
            message_obj = Message.objects.create(
                content=data["content"],
                user=user_obj,
                chat=chat_obj
                )
        serializer = MessageSerializer(message_obj)
        data = success_response(serializer.data)
        return Response((data))
    
    
    
    def update(self, request, *args, **kwargs):
        print("updating ...")
        data = request.data
        pk = kwargs["pk"]
        chat_message_obj =None
        if pk:
            pk = int(pk)
        try:
            chat_message_obj =  Message.objects.get(pk=pk)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Chat Message")
            return Response(res, content_type="application/json")
      
        if data.get("content"):
            print("data ===",data["content"])
            chat_message_obj.content = data["content"]
        else:
            pass
        chat_message_obj.save()
        serializer = MessageSerializer(chat_message_obj)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = Message.objects.filter(id=str(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "Chat Message")
            return Response(res, content_type="application/json")
        instance.delete()
        return Response({"result": "Chat instance was successfuly deleted!"})

