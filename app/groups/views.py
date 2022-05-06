from core.models import (
    Advisor,
    Batch,
    Examiner,
    Group,
    Member,
    ProjectTitle,
    Student,
    User,
)
from core.permissions import (
    HasGroup,
    IsAdmin,
    IsAdminOrReadOnly,
    IsCoordinatorOrReadOnly,
    IsReadOnly,
    IsStaff,
    IsStudent,
    IsStudentOrReadOnly,
)
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from groups.serializers import (
    GroupSerializer,
    MemberSerializer,
    ProjectTitleSerializer,
    ReadAdvisorSerializer,
    ReadExaminerSerializer,
    ReadGroupSerializer,
    ReadMembersSerializer,
    WriteAdvisorSerialzer,
    WriteExaminerSerialzer,
)


class GroupsModelViewSet(ModelViewSet):
    filterset_fields = ["batch", "group_name"]
    queryset = Group.objects.all()

    permission_classes = [
        IsStudentOrReadOnly,
    ]

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
            # return Response({"hello": "helopp"})
        except Member.DoesNotExist:
            return Response({"error": "your are not authorized to edit the group"})


class MemberModelViewSet(ModelViewSet):

    permission_classes = (IsStudentOrReadOnly,)
    queryset = Member.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReadMembersSerializer
        return MemberSerializer

    def create(self, request, group_pk=None):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response

        group = get_object_or_404(Group.objects, pk=group_pk)
        user = get_object_or_404(User.objects, username=request.data["member"])
        get_object_or_404(Student.objects, user=user.pk)

        request.data["group"] = group.pk
        request.data["member"] = user.pk
        return super(MemberModelViewSet, self).create(request)

    def update(self, request, group_pk=None, *args, **kwargs):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response
        group = get_object_or_404(Member.objects, pk=group_pk)
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
            # return Response({"hello": "helopp"})
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


# class ProjectTitleViewSet(ModelViewSet):
#     permission_classes = [IsStudent, IsReadOnly]
#     serializer_class = ProjectTitleSerializer

#     def get_queryset(self):
#         projecttitles = ProjectTitle.objects.all()
#         return projecttitles

class ProjectTitleModelViewSet(ModelViewSet):

    permission_classes = (IsStudentOrReadOnly,)
    queryset = ProjectTitle.objects.all()

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReadMembersSerializer
        return MemberSerializer

    def create(self, request, group_pk=None):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response
        group = get_object_or_404(Group.objects, pk=group_pk)
        user = get_object_or_404(User.objects, username=request.data["member"])
        member = get_object_or_404(Student.objects, pk=user.pk)

        request.data["group"] = group.pk
        request.data["member"] = member.pk
        return super(MemberModelViewSet, self).create(request)

    def update(self, request, group_pk=None, *args, **kwargs):
        response = self.check_membership(request, group_pk)
        if response != None:
            return response
        group = get_object_or_404(Member.objects, pk=group_pk)
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
            # return Response({"hello": "helopp"})
        except Member.DoesNotExist:
            return Response({"error": "your are not authorized to edit or view the group"})



