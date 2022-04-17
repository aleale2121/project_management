import json

from constants.constants import MODEL_ALREADY_EXIST, MODEL_RECORD_NOT_FOUND
from core.models import Batch, Examiner, Member, StudentEvaluation, SubmissionDeadLine, SubmissionType
from django.db import transaction
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from pkg.util import error_response, success_response
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .serializer import SubmissionDeadLineSerializer


class SubmissionDeadLineViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionDeadLineSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["name", "batch", "dead_line"]
    search_fields = ["name", "batch", "dead_line"]
    filter_fields = ["name", "batch", "dead_line"]

    def get_queryset(self):
        evaluations = SubmissionDeadLine.objects.all()
        return evaluations

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("creating ...")
        data = request.data
        global submission_type_obj
        global batch_obj
        try:
            submission_type_obj = SubmissionType.objects.get(name=data["name"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "SubmissionType")
            return Response(res, content_type="application/json")
        try:
            batch_obj = Batch.objects.get(name=data["batch"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Batch")
            return Response(res, content_type="application/json")

        count = SubmissionDeadLine.objects.filter(name=submission_type_obj, batch=batch_obj).count()
        print("Count ", count)
        if count > 0:
            res = error_response(request, MODEL_ALREADY_EXIST, "SubmissionDeadLine")
            return Response(res, content_type="application/json")
        else:
            pass

        new_sub_dead_line_obj = SubmissionDeadLine.objects.create(
            name=submission_type_obj, batch=batch_obj, dead_line=data["dead_line"]
        )

        serializer = SubmissionDeadLineSerializer(new_sub_dead_line_obj)
        data = success_response(serializer.data)
        return Response((data))

    def update(self, request, *args, **kwargs):
        print("updating ...")
        data = request.data
        pk = kwargs["pk"]
        if pk:
            pk = int(pk)
        sub_dead_line = SubmissionDeadLine.objects.get(pk=pk)

        if data.get("name"):
            sub_dead_line.name = data["name"]
        else:
            pass

        if data.get("batch"):
            sub_dead_line.batch = data["batch"]
        else:
            pass

        if data.get("dead_line"):
            sub_dead_line.dead_line = data["dead_line"]
        else:
            pass

        sub_dead_line.save()
        print("updated.")
        serializer = SubmissionDeadLineSerializer(sub_dead_line)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = SubmissionDeadLine.objects.filter(id=int(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "SubmissionDeadLine")
            return Response(res, content_type="application/json")
        instance.delete()
        return Response({"result": "SubmissionDeadLine instance was successfuly deleted!"})
