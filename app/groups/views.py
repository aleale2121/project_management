import json
from tokenize import group
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.permissions import SAFE_METHODS

import requests
from constants.constants import MODEL_RECORD_NOT_FOUND, MODEL_UPDATE_FAILED
from core.models import (
    Advisor,
    Batch,
    Examiner,
    Group,
    Member,
    ProjectTitle,
    Student,
    TitleDeadline,
    
    User,
)
from core.permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsCoordinatorOrReadOnly,
    IsCoordinatorOrStudentReadOnly,
    IsStaffOrReadOnly,
    IsStudent,
    IsStudentOrReadOnly,
    PermissionPolicyMixin,
)
from django.db import transaction
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from pkg.util import error_response
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from django.conf import settings

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


class GroupsModelViewSet(PermissionPolicyMixin, ModelViewSet):
    filterset_fields = ["batch", "group_name"]
    queryset = Group.objects.all()
    permission_classes = [
        IsCoordinatorOrReadOnly,
    ]
    permission_classes_per_method = {
        # except for list and retrieve where both users with "write" or "read-only"
        # permissions can access the endpoints.
        "create": [IsStudent]
    }

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReadGroupSerializer
        return GroupSerializer

    def update(self, request, *args, **kwargs):
        self.methods = ("put",)
        response = self.check_membership(request, kwargs["pk"])
        if response != None:
            return response
        return super(self.__class__, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        response = self.check_membership(request, kwargs["pk"])
        if response != None:
            return response
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
        detail=False,
        methods=["GET"],
        permission_classes=[IsStudent],
        # url_path="(?P<batch>[^/.]+)",
    )
    def mygroup(self, request):
        groups_list = ReadGroupSerializer(Group.objects.filter(members__member__exact=request.user), many=True)
        return Response(groups_list.data)


class MemberModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsCoordinatorOrReadOnly]
    queryset = Member.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReadMembersSerializer
        return MemberSerializer

    @transaction.atomic
    def create(self, request, group_pk=None):
        # response = self.check_membership(request, group_pk)
        # if response != None:
        #     return response

        group = get_object_or_404(Group.objects, pk=group_pk)
        user = get_object_or_404(User.objects, username=request.data["member"])
        get_object_or_404(Student.objects, user=user.pk)

        request.data["group"] = group.pk
        request.data["member"] = user.pk

        return super(MemberModelViewSet, self).create(request)

    def update(self, request, group_pk=None, *args, **kwargs):
        # response = self.check_membership(request, group_pk)
        # if response != None:
        #     return response
        group = Member.objects.get(id=group_pk)
        request.data["group"] = group.pk
        return super(MemberModelViewSet, self).update(request, *args, **kwargs)

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
        # response = self.check_membership(request, group_pk)
        # if response != None:
        #     return response
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


@api_view(["GET"])
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
        "comparableProjects": filtered,
    }
    response = requests.post(
        "https://sfpm-check-similarity-backend.herokuapp.com/api/check-similarity",
        data=json.dumps(payload),
        headers={
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        },
    )
    print("\n similarity \n")
    checkedProjects = response.json()
    similarProjects = []
    for pro in checkedProjects:
        for fPrj in allProjects:
            if fPrj.id == pro["id"]:
                proDict = model_to_dict(fPrj)
                proDict["similarity"] = pro["similarity"]
                similarProjects.append(proDict)
    return Response(
        {
            "project_title": model_to_dict(title),
            "similarProjects": similarProjects,
        }
    )


@api_view(["PATCH"])
@permission_classes([IsCoordinatorOrReadOnly])
def approve_title(request, pk):
    title = get_object_or_404(ProjectTitle.objects, pk=pk)
    ProjectTitle.objects.filter(group=title.group).update(
        status=ProjectTitle.STATUS_CHOICES.REJECTED,
    )
    title=ProjectTitle.objects.filter(pk=pk).update(
        status=ProjectTitle.STATUS_CHOICES.APPROVED,
    )
    ProjectTitle.objects.filter(group=title.group).delete(
        status=ProjectTitle.STATUS_CHOICES.REJECTED,
    )
    return Response(model_to_dict(ProjectTitle.objects.get(pk=title)))


@api_view(["PATCH"])
@permission_classes([IsCoordinatorOrReadOnly])
def reject_title(request, pk):
    title = get_object_or_404(ProjectTitle.objects, pk=pk)
    title=ProjectTitle.objects.filter(pk=pk).delete()    
    return Response(model_to_dict(ProjectTitle.objects.get(pk=title)))


class ProjectTitleModelViewSet(ModelViewSet):

    permission_classes = (IsStudentOrReadOnly,)
    queryset = ProjectTitle.objects.all()
    filterset_fields = ["group", "status"]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReadProjectTitleSerializer
        return WriteProjectTitleSerializer

    def list(self, request, group_pk=None):
        status_param= self.request.query_params.get('status')
        queryset = ProjectTitle.objects.filter(group=group_pk)
        if(status_param !=None):
            queryset = queryset.filter(status=status_param)
        serializer = ReadProjectTitleSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, group_pk=None):
        status_param= self.request.query_params.get('status')
        queryset = ProjectTitle.objects.filter(pk=pk, group=group_pk)
        if(status_param !=None):
            queryset = queryset.filter(status=status_param)
        group = get_object_or_404(queryset, pk=pk)
        serializer = ReadProjectTitleSerializer(group)
        return Response(serializer.data)

    def create(self, request, group_pk=None):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response
        resp= self.check_deadline(request)
        if resp!=None:
            return resp

        group = get_object_or_404(Group.objects, pk=group_pk)
        title = None
        try:
            title = ProjectTitle.objects.get(group=group, no=request.data["no"])
            if title != None:
                return Response(
                    {
                        "error": "project title " + str(request.data["no"]) + " already submitted",
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
        response = super(ProjectTitleModelViewSet, self).create(request)
        data = response.data

        return Response(
            {
                "project_title": data,
            }
        )

    def update(self, request, group_pk=None, *args, **kwargs):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response

        resp= self.check_deadline(request)
        if resp!=None:
            return resp
        group = get_object_or_404(Group.objects, pk=group_pk)
        request.data["group"] = group
        return super(ProjectTitleModelViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, pk=None, group_pk=None):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response
        resp= self.check_deadline(request)
        if resp!=None:
            return resp
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
    
    def check_deadline(self, request):
        if not request.method in SAFE_METHODS:
            active_batch = None
            try:
                active_batch = Batch.objects.get(is_active=True)
            except Batch.DoesNotExist:
                return Response(
                    {"error": "there is no active batch"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if request.method == "POST" or request.method == "UPDATE" or request.method == "PATCH":
                deadline = None
                try:
                    deadline = TitleDeadline.objects.get(batch=active_batch)
                    now_time = timezone.now()

                    if now_time >= deadline.deadline:
                        return Response(
                            {"error": "submission date is closed"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                except TitleDeadline.DoesNotExist:

                    return Response(
                        {"error": "submission date is not open"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                get_object_or_404(ProjectTitle, id=self.kwargs["pk"])
                deadline = None
                try:
                    deadline = TitleDeadline.objects.get(
                        batch=active_batch,
                    )
                    now_time = timezone.now()
                    if now_time>= deadline.deadline:
                        return Response(
                            {"error": "title submission date is closed"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                except TitleDeadline.DoesNotExist:
                    return Response(
                        {"error": "title submission date is not open"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )