from datetime import datetime
from django.utils import timezone

from constants.constants import MODEL_ALREADY_EXIST, MODEL_RECORD_NOT_FOUND
from core.models import Batch, Group, Member, Student, Submission, SubmissionDeadLine
from core.permissions import IsStudentOrReadOnly, IsStudentOrReadOnlyAndGroupMember
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from submissions.serializers import SubmissionsSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionsSerializer
    permission_classes = [IsStudentOrReadOnlyAndGroupMember]
    queryset = Submission.objects.all()
    filterset_fields = ["submissionType", "group"]

    def create(self, request, *args, **kwargs):
        resp= self.check_deadline(request, *args, **kwargs)
        if resp!=None:
            return resp

        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        resp= self.check_deadline(request, *args, **kwargs)
        if resp!=None:
            return resp
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        resp= self.check_deadline(request, *args, **kwargs)
        if resp!=None:
            return resp
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        resp= self.check_deadline(request, *args, **kwargs)
        if resp!=None:
            return resp
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    def check_deadline(self, request, *args, **kwargs):

        if not request.method in SAFE_METHODS:
            print("1****hello")
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
                    deadline = SubmissionDeadLine.objects.get(name=request.data["submissionType"], batch=active_batch)
                    now_time = timezone.now()

                    if now_time >= deadline.dead_line:
                        return Response(
                            {"error": "submission date is closed"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                except SubmissionDeadLine.DoesNotExist:

                    return Response(
                        {"error": "submission date is not open"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                submission = get_object_or_404(Submission, id=self.kwargs["pk"])
                deadline = None
                try:
                    deadline = SubmissionDeadLine.objects.get(
                        name=submission.submissionType,
                        batch=active_batch,
                    )
                    now_time = timezone.now()
                    if now_time>= deadline.dead_line:
                        return Response(
                            {"error": "submission date is closed"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                except SubmissionDeadLine.DoesNotExist:
                    return Response(
                        {"error": "submission date is not open"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
