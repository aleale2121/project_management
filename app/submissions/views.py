from constants.constants import MODEL_ALREADY_EXIST, MODEL_RECORD_NOT_FOUND
from core.models import Group, Member, Student, Submission
from core.permissions import IsStudentOrReadOnly, IsStudentOrReadOnlyAndGroupMember
from rest_framework import viewsets
from rest_framework.response import Response

from submissions.serializers import SubmissionsSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionsSerializer
    permission_classes = [IsStudentOrReadOnlyAndGroupMember]
    queryset = Submission.objects.all()
    
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
