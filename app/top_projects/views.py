import json
from urllib.request import proxy_bypass

from constants.constants import FORBIDDEN_REQUEST_FOUND, MODEL_ALREADY_EXIST, MODEL_CREATION_FAILED, MODEL_PARAM_MISSED, MODEL_RECORD_NOT_FOUND
from core.models import  Batch, Group, ProjectTitle, TopProject,User, Voter,NumberOfVoter
from django.db import transaction
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from pkg.util import error_response, success_response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from core.permissions import IsAdmin, IsCoordinatorOrReadOnly
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
    # permission_classes=[IsCoordinatorOrReadOnly]
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
            return Response(res, status=int(res['status_code']),content_type="application/json")
        try:
            batch_obj = Batch.objects.get(name=form_data["batch"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Batch")
            return Response(res, status=int(res['status_code']),content_type="application/json")
        try:
            group_obj = Group.objects.get(id=form_data["group"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Group")
            return Response(res, status=int(res['status_code']),content_type="application/json")
        try:
            title_obj = ProjectTitle.objects.get(id=form_data["id"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Title")
            return Response(res,status=int(res['status_code']), content_type="application/json")

        
        project_obj = TopProject.objects.create(
            group=group_obj,
            batch=batch_obj,
            title=title_obj,
            description=form_data["description"]
        )
        serializer = TopProjectSerializer(project_obj)
        data = success_response(serializer.data)
        return Response((data))
    
    def retrieve(self, request, pk=None):
        if not pk.isdigit():
            res = error_response(request, MODEL_PARAM_MISSED, "TopProject")
            res['message']='Invalid request parameter found.'
            return Response(res,status=int(res['status_code']), content_type="application/json")
        try:
            queryset = TopProject.objects.get(pk=pk)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "TopProject")
            res['message']='TopProject not found with id '+pk+"."
            return Response(res,status=int(res['status_code']), content_type="application/json")
        serializer=TopProjectSerializer(queryset)
        return Response(serializer.data)
    @action(
        detail=True,
        methods=["PUT"],
        url_path="vote",
    )
    def vote(self, request,*args, **kwargs):
        print("updating ...")
        pk = int(kwargs["pk"])
        usr = int(request.user.id)
        print("pk ",pk,"usr =>",usr)
        voter_count=0
        top_project_obj = None
        user_obj = None
        logged_usr=None
        is_staff=False
        is_student=False
        try:
            logged_usr = User.objects.get(id=int(usr))
            is_staff=logged_usr.is_staff
            is_student=logged_usr.is_student
            print("is_staff =>",is_staff,"is_student =>",is_student)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
            res['message']='Voter seems anonymous user.'
            return Response(res, status=int(res['status_code']),content_type="application/json")
        print("voter_count==>",voter_count)
        if Voter.objects.filter(user_id=logged_usr).exists():
            print("line ---132")
            voter = Voter.objects.get(user_id=logged_usr)
            if voter.user_id.id == usr and voter.project_id.id == pk:
                print("line-106")
                TopProject.objects.filter(id=pk).update(vote=F('vote')-1)
                if (is_staff==True):
                    self.decrement_staff(pk)
                if (is_student==True):
                    self.decrement_student(pk)
                    
                Voter.objects.filter(user_id=logged_usr,project_id=pk).delete()
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
                    return Response(res,status=int(res['status_code']), content_type="application/json")
                try:
                    top_project_obj = TopProject.objects.get(id=pk)
                except:
                    res = error_response(request, MODEL_RECORD_NOT_FOUND, "TopProject")
                    return Response(res,status=int(res['status_code']), content_type="application/json")
                Voter.objects.create(user_id=user_obj,project_id=top_project_obj)
                TopProject.objects.filter(id=pk).update(vote=F('vote')+1)
                if (is_staff==True):
                    self.decrement_staff(pk)
                if (is_student==True):
                    self.decrement_student(pk)
                return Response({"message":"You Voted Successfully!"})

            else:
                print("line---170")
                pass
        else:
            print("line-173")
            top_project_obj = TopProject.objects.filter(id=pk).update(vote=F('vote')+1)
            try:
                user_obj = User.objects.get(id=usr)
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
                res['message']='No logged user found!'
                return Response(res,status=int(res['status_code']), content_type="application/json")
            try:
                top_project_obj = TopProject.objects.get(id=pk)
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "TopProject")
                res['message']='No TopProject found for voting.'
                return Response(res,status=int(res['status_code']), content_type="application/json")
            
            Voter.objects.create(
                user_id=user_obj,
                project_id=top_project_obj
                )
            if NumberOfVoter.objects.filter(project=top_project_obj).exists():
                pass
            else:
                NumberOfVoter.objects.create(project=top_project_obj)
            if (is_staff==True):
                self.increment_staff(pk)
            if (is_student==True):
                self.increment_student(pk)
            return Response({"message":"You Voted Successfully!"})
            
            
    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = TopProject.objects.filter(id=int(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "TopProject")
            return Response(res, status=int(res['status_code']),content_type="application/json")
        instance.delete()
        return Response({"result": "TopProject instance was successfuly deleted!"})
    
    
    
    def is_exists(self,project_id):
        if NumberOfVoter.objects.filter(project=project_id).exists():
            return True
        else:
            return False
    def increment_staff(self,project_id):
        NumberOfVoter.objects.filter(project=project_id).update(staffs=F('staffs')+1)
        
    def decrement_staff(self,project_id):
        NumberOfVoter.objects.filter(project=project_id).update(staffs=F('staffs')-1)
        
    def increment_student(self,project_id):
        NumberOfVoter.objects.filter(project=project_id).update(students=F('students')+1)

    def decrement_student(self,project_id):
        NumberOfVoter.objects.filter(project=project_id).update(students=F('students')-1)   
    def get_to_project_object(self,project_id):
        top_proj=TopProject.objects.filter(id=project_id)[0]
        return top_proj
         
        
      