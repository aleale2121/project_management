import json
from urllib.request import proxy_bypass

from constants.constants import FORBIDDEN_REQUEST_FOUND, MODEL_ALREADY_EXIST, MODEL_CREATION_FAILED, MODEL_RECORD_NOT_FOUND
from core.models import  Batch, Group, ProjectTitle, TopProject,User,Title, Voter
from django.db import transaction
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from pkg.util import error_response, success_response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from core.permissions import IsAdmin
from django.db.models import F
from rest_framework.decorators import action
from django.db.models import  Sum
# from django.core import serializers

from .serializer import TopProjectSerializer,VoterSerializer
class TopProjectFilter(filters.FilterSet):
    project_id = filters.NumberFilter(field_name="project_id")
    user_id = filters.NumberFilter(field_name="user_id")
    group = filters.NumberFilter(field_name="group")
    batch = filters.CharFilter(field_name="batch")

    class Meta:
        model = TopProject
        fields = ["title", "batch", "group","doc_path","vote","description","is_approved"]


class TopProjectViewSet(viewsets.ModelViewSet):
    serializer_class = TopProjectSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_class = TopProjectFilter
    ordering_fields = ["batch", "group"]
    search_fields = ["batch", "group"]
    filterset_fields = [
        "batch","group","id"
    ]
    queryset=None
    def get_queryset(self):
        print("fetching ...")
        queryset = TopProject.objects.all().order_by('id')
        return queryset
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("creating ...")
        form_data = request.data
        global user_obj
        global project_obj
        global batch_obj
        global title_obj
        global group_obj
        usr=self.request.user.id
        print("user id =>",usr)
        try:
            user_obj = User.objects.get(id=int(usr))
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
            return Response(res, content_type="application/json")
        try:
            batch_obj = Batch.objects.get(name=form_data["batch"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Batch")
            return Response(res, content_type="application/json")
        try:
            group_obj = Group.objects.get(id=form_data["group"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Group")
            return Response(res, content_type="application/json")
        try:
            title_obj = ProjectTitle.objects.get(id=form_data["id"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Title")
            return Response(res, content_type="application/json")

        
        project_obj = TopProject.objects.create(
            group=group_obj,
            batch=batch_obj,
            title=title_obj,
            description=form_data["description"]
        )
        serializer = TopProjectSerializer(project_obj)
        data = success_response(serializer.data)
        return Response((data))
    @action(
        detail=True,
        methods=["PUT"],
        permission_classes=[IsAdmin],
        url_path="vote",
    )
    def vote(self, request,*args, **kwargs):
        print("updating ...")
        pk = int(kwargs["pk"])
        usr=self.request.user.id
        voter_count=0
        top_project_obj = None
        user_obj = None
        voter_count = Voter.objects.filter(user_id=usr).count()
        if voter_count==1:
            voter = Voter.objects.get(user_id=usr)
            # print("User Information => ","user_id ->",voter.user_id.id,"project_id ->",voter.project_id.id,"pk ->",pk," voter.project_id.id != pk ->" ,voter.project_id.id != pk)
            if voter.user_id.id == usr and voter.project_id.id == pk:
                print("line-106")
                TopProject.objects.filter(id=pk).update(vote=F('vote')-1)
                Voter.objects.filter(user_id=usr,project_id=pk).delete()
                return Response({"message":"You unvoted successfully!"})
                
            elif (voter.user_id.id == usr and voter.project_id.id != pk):
                print("line-111")
                TopProject.objects.filter(id=voter.project_id.id).update(vote=F('vote')-1)
                Voter.objects.filter(user_id=voter.user_id.id,project_id=voter.project_id.id).delete()
                print("line-113")
                try:
                    user_obj = User.objects.get(id=usr)
                except:
                    res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
                    return Response(res, content_type="application/json")
                try:
                    top_project_obj = TopProject.objects.get(id=pk)
                except:
                    res = error_response(request, MODEL_RECORD_NOT_FOUND, "TopProject")
                    return Response(res, content_type="application/json")
                Voter.objects.create(user_id=user_obj,project_id=top_project_obj)
                TopProject.objects.filter(id=pk).update(vote=F('vote')+1)
                return Response({"message":"You Voted Successfully!"})

            else:
                print("line-132")
                pass
        else:
            print("line-119")
            top_project_obj = TopProject.objects.filter(id=pk).update(vote=F('vote')+1)
            try:
                user_obj = User.objects.get(id=usr)
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
                return Response(res, content_type="application/json")
            try:
                top_project_obj = TopProject.objects.get(id=pk)
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "TopProject")
                return Response(res, content_type="application/json")
            Voter.objects.create(user_id=user_obj,project_id=top_project_obj)
            return Response({"message":"You Voted Successfully!"})
            
    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = TopProject.objects.filter(id=int(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "TopProject")
            return Response(res, content_type="application/json")
        instance.delete()
        return Response({"result": "TopProject instance was successfuly deleted!"})
