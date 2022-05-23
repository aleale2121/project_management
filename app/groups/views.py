from constants.constants import MODEL_RECORD_NOT_FOUND, MODEL_UPDATE_FAILED
from pkg.util import error_response
import json
from django.forms.models import model_to_dict
import requests
from core.models import (
    Advisor,
    Batch,
    Examiner,
    ProjectTitle,
    Group,
    Member,
    Student,
    Title,
    User,
)
from core.permissions import IsCoordinatorOrReadOnly, IsStudentOrReadOnly
from core.permissions import IsCoordinatorOrReadOnly, IsStaffOrReadOnly, IsStudentOrReadOnly
from django.core import serializers as coreSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db import transaction
from rest_framework.decorators import action
from core.permissions import IsAdmin, IsAdminOrReadOnly

from rest_framework.decorators import action, api_view, permission_classes


from groups.serializers import (
    GroupSerializer,
    MemberSerializer,
    ReadAdvisorSerializer,
    ReadExaminerSerializer,
    ReadGroupSerializer,
    ReadMembersSerializer,
    ReadProjectTitleFromMapSerializer,
    ReadProjectTitleSerializer,
    WriteAdvisorSerialzer,
    WriteExaminerSerialzer,
    WriteProjectTitleSerializer,
)


class GroupsModelViewSet(ModelViewSet):
    filterset_fields = ["batch", "group_name"]
    queryset = Group.objects.all()
    permission_classes = [IsStudentOrReadOnly,]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReadGroupSerializer
        return GroupSerializer

    def update(self, request, *args, **kwargs):
        print("updating ..")
        self.methods = ("put",)
        response = self.check_membership(request, kwargs["pk"])
        if response != None:
            return response
        return super(self.__class__, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # response = self.check_membership(request, kwargs["pk"])
        # if response != None:
        #     return response
        try:
            instance = self.get_object()
            self.perform_destroy(
                instance,
            )
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        
        instance.delete()

    def check_membership(self, request, id):
        student = None
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"error": "you are not student"})
        group = None
        try:
            group = Group.objects.get(id=id)
        except Group.DoesNotExist:
            return Response({"error": "group doesnot exist"})
        try:
            member = Member.objects.get(group=group, member=request.user)
        except Member.DoesNotExist:
            return Response({"error": "your are not authorized to edit the group"})
    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAdmin],
        url_path="(?P<batch>[^/.]+)",
    )
    def assignTitle(self,request,pk=None,batch=None):
        print("assign Title to groups",pk,batch)
        title_obj=None
        try:
              title_obj=ProjectTitle.objects.get(id=request.data['title'])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Title")
            return Response(res, content_type="application/json")
        try:
            group=Group.objects.get(id=pk,batch=batch)
            group.title=title_obj
            group.save()
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Group")
            return Response(res, content_type="application/json")
        serializer=GroupSerializer(group)
        return Response(serializer.data)

class MemberModelViewSet(ModelViewSet):
    permission_classes = (IsStudentOrReadOnly,)
    queryset = Member.objects.all()
    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReadMembersSerializer
        return MemberSerializer
    @transaction.atomic
    def create(self, request, group_pk=None):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response

        group = get_object_or_404(Group.objects, pk=group_pk)
        user = get_object_or_404(User.objects, username=request.data["member"])
        get_object_or_404(Student.objects, user=user.pk)

        request.data["group"] = group.pk
        request.data["member"] = user.pk
        return super(ProjectTitleModelViewSet, self).create(request)

    def update(self, request, group_pk=None, *args, **kwargs):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response
        group = Member.objects.get(id=group_pk)
        request.data["group"] = group.pk
        return super(ProjectTitleModelViewSet, self).update(request, *args, **kwargs)

    def list(self, request, group_pk=None):
        queryset = Member.objects.filter(group=group_pk)
        serializer = ReadMembersSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, group_pk=None):

        queryset = Member.objects.filter(pk=pk, group=group_pk)
        group = get_object_or_404(queryset, pk=pk)
        serializer = ReadMembersSerializer(group)
        return Response(serializer.data)

    def destroy(self, request, pk=None, group_pk=None):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response
        member = get_object_or_404(self.queryset, pk=pk, group__pk=group_pk)
        self.perform_destroy(member)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def check_membership(self, request, id):
        student = None
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"error": "you are not student"})

        group = None
        try:
            group = Group.objects.get(id=id)
        except Group.DoesNotExist:
            return Response({"error": "group doesnot exist"})

        try:
            member = Member.objects.get(group=group, member=request.user)
        except Member.DoesNotExist:
            return Response({"error": "your are not authorized to edit or view the group"})


class AdvisorModelViewSet(ModelViewSet):
    permission_classes = [IsCoordinatorOrReadOnly]
    queryset = Advisor.objects.all()
    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReadAdvisorSerializer
        return WriteAdvisorSerialzer
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Advisor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()


class ExaminerModelViewSet(ModelViewSet):
    permission_classes = [IsCoordinatorOrReadOnly]
    def get_queryset(self):
        return Examiner.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReadExaminerSerializer
        return WriteExaminerSerialzer
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Examiner.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()

@api_view(['GET'])
def similarity_check(request, pk):
    title = get_object_or_404(ProjectTitle.objects, pk=pk)
    
    allProjects = ProjectTitle.objects.all()
    filtered = []
    for prj in allProjects:
        if prj.id != title.id:
            filtered.append({"id": prj.id, "description": prj.title_description})
    payload = {
        "project": {
            "id": title.id,
            "description": title.title_description,
        },
        "comparableProjects":filtered
    }
    response = requests.post(
        "https://sfpm-check-similarity-backend.herokuapp.com/api/check-similarity",
        data=json.dumps(payload),
        headers={
            'Content-Type':'application/json',
            'Accept':'*/*',
            'Accept-Encoding':'gzip, deflate, br',
            'Connection':'keep-alive'
        }
    )
    print("\n similarity \n")
    checkedProjects =  response.json()
    similarProjects = []
    for pro in checkedProjects:
        for fPrj in allProjects:
            if fPrj.id == pro['id']:
                proDict=model_to_dict(fPrj)
                proDict['similarity']=pro['similarity']
                similarProjects.append(proDict)
    return Response({
        'project_title':model_to_dict( title ),
        'similarProjects':similarProjects,
    })



class ProjectTitleModelViewSet(ModelViewSet):

    permission_classes = (IsStudentOrReadOnly,)
    queryset = ProjectTitle.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReadProjectTitleSerializer
        return WriteProjectTitleSerializer

    def create(self, request, group_pk=None):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response

        group = get_object_or_404(Group.objects, pk=group_pk)
        title = None
        try:
            title = ProjectTitle.objects.get(group=group, no=request.data["no"])
            if title != None:
                return Response(
                    {
                        "error": "project title " + str(request.data["no"]) +
                        " already submitted",
                    }
                )
        except KeyError:
            return Response(
                {
                    "error": "no field is required",
                }
            )
        except ProjectTitle.DoesNotExist:
            pass
        request.data["group"] = group
        response= super(ProjectTitleModelViewSet, self).create(request)
        print("new title \n")
        data=response.data
        # serializer=ReadProjectTitleFromMapSerializer(response.data)
        newtitle= ProjectTitle(
            id=data['id'],
            title_name=data['title_name'],
            no=data['no'],  
            title_description=data['title_description'], 
            status=data['status'], 
            rejection_reason=data['rejection_reason'], 
        )
        print(newtitle)
        print("new title \n")

        allProjects = ProjectTitle.objects.all()
        filtered = []
        for prj in allProjects:
            if prj.id != newtitle.id:
                filtered.append({"id": prj.id, "description": prj.title_description})
        payload = {
            "project": {
                "id": newtitle.id,
                "description": newtitle.title_description,
            },
            "comparableProjects":filtered
        }
        response = requests.post(
            "https://sfpm-check-similarity-backend.herokuapp.com/api/check-similarity",
            data=json.dumps(payload),
            headers={
                'Content-Type':'application/json',
                'Accept':'*/*',
                'Accept-Encoding':'gzip, deflate, br',
                'Connection':'keep-alive'
            }
        )
        print("\n similarity \n")
        checkedProjects =  response.json()
        similarProjects = []
        for pro in checkedProjects:
            for fPrj in allProjects:
                if fPrj.id == pro['id']:
                    proDict=model_to_dict(fPrj)
                    proDict['similarity']=pro['similarity']
                    similarProjects.append(proDict)
        return Response({
            'project_title':model_to_dict( newtitle ),
            'similarProjects':similarProjects,
        })


    def update(self, request, group_pk=None, *args, **kwargs):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response
        group = get_object_or_404(Group.objects, pk=group_pk)
        request.data["group"] = group
        return super(ProjectTitleModelViewSet, self).update(request, *args, **kwargs)

    def list(self, request, group_pk=None):

        queryset = ProjectTitle.objects.filter(group=group_pk)
        serializer = ReadProjectTitleSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, group_pk=None):

        queryset = ProjectTitle.objects.filter(pk=pk, group=group_pk)
        group = get_object_or_404(queryset, pk=pk)
        serializer = ReadProjectTitleSerializer(group)
        return Response(serializer.data)

    def destroy(self, request, pk=None, group_pk=None):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response
        member = get_object_or_404(self.queryset, pk=pk, group__pk=group_pk)
        self.perform_destroy(member)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def check_membership(self, request, id):
        try:
            Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return Response({"error": "you are not student"})

        group = None
        try:
            group = Group.objects.get(id=id)
        except Group.DoesNotExist:
            return Response({"error": "group doesnot exist"})

        try:
            Member.objects.get(group=group, member=request.user)
        except Member.DoesNotExist:
            return Response({"error": "your are not authorized to edit or view the group"})
