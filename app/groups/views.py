from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from core.models import Advisor, Examiner, Group
from groups.serializers import ReadExaminerSerializer, WriteAdvisorSerialzer,ReadAdvisorSerializer, GroupSerializer, WriteExaminerSerialzer
from core.permissions import IsAdmin, IsAdminOrReadOnly, IsStaff, IsStudent


class GroupsModelViewSet(ModelViewSet):
    queryset = Group.objects.all()

    permission_classes = [IsAdmin]
    serializer_class = GroupSerializer


class AdvisorModelViewSet(ModelViewSet):

    permission_classes = [IsAdmin]
    queryset=Advisor.objects.all()
    # def get_queryset(self):
    #     return Advisor.objects.all()
 
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

    permission_classes = [IsAdmin]

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