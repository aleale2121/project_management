import json

from constants.constants import MODEL_ALREADY_EXIST, MODEL_RECORD_NOT_FOUND
from core.models import Examiner, Member, StudentEvaluation, SubmissionType
from django.db import transaction
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from pkg.util import error_response, success_response
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .serializer import StudentEvaluationSerializer


class StudentEvaluationFilter(filters.FilterSet):
    member = filters.NumberFilter(field_name="member")
    assesment = filters.CharFilter(field_name="submission_type")
    examiner = filters.NumberFilter(field_name="examiner")
    group = filters.NumberFilter(field_name="member__group")
    group_name = filters.CharFilter(field_name="member__group__group_name")
    student_id = filters.NumberFilter(field_name="member__member")
    student_username = filters.NumberFilter(field_name="member__member__username")
    examiner__group = filters.NumberFilter(field_name="member__group")
    examiner_id = filters.NumberFilter(field_name="examiner__examiner")
    examiner_username = filters.NumberFilter(field_name="examiner__examiner__username")
    batch = filters.CharFilter(field_name="member__group__batch")

    class Meta:
        model = StudentEvaluation
        fields = ["member", "submission_type", "examiner"]


class StudentEvaluaionViewSet(viewsets.ModelViewSet):
    serializer_class = StudentEvaluationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_class = StudentEvaluationFilter
    ordering_fields = ["examiner", "submission_type", "member"]
    search_fields = ["examiner", "submission_type", "member"]

    def get_queryset(self):
        print("fetching ...")
        evaluations = StudentEvaluation.objects.all()
        return evaluations

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("creating ...")
        evaluation_data = request.data
        global submission_type_obj
        global member_obj
        global student_obj
        global examiner_obj
        global new_student_obj
        for data in evaluation_data:
            try:
                member_obj = Member.objects.get(id=data["member"])
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "Member")
                return Response(res, content_type="application/json")
            try:
                submission_type_obj = SubmissionType.objects.get(name=data["submission_type"])
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "SubmissionType")
                return Response(res, content_type="application/json")
            try:
                examiner_obj = Examiner.objects.get(id=data["examiner"])
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "Examiner")
                return Response(res, content_type="application/json")
            count = StudentEvaluation.objects.filter(
                submission_type=submission_type_obj, examiner=examiner_obj, member=member_obj
            ).count()

            if count > 0:
                res = error_response(request, MODEL_ALREADY_EXIST, "StudentEvaluation")
                return Response(res, content_type="application/json")
            else:
                pass
            new_student_obj = StudentEvaluation.objects.create(
                submission_type=submission_type_obj,
                examiner=examiner_obj,
                member=member_obj,
                mark=data["mark"],
                comment=data["comment"],
            )

        serializer = StudentEvaluationSerializer(new_student_obj)
        data = success_response(serializer.data)
        return Response((data))

    def update(self, request, *args, **kwargs):
        print("updating ...")
        data = request.data
        print(type(data))
        pk = kwargs["pk"]
        if pk:
            pk = int(pk)
        student_result = StudentEvaluation.objects.get(pk=pk)

        if data.get("comment"):
            student_result.comment = data["comment"]
        else:
            pass
        if data.get("mark"):
            student_result.mark = float(data["mark"])
        else:
            pass
        student_result.save()
        print("updated.")
        serializer = StudentEvaluationSerializer(student_result)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = StudentEvaluation.objects.filter(id=int(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "StudentEvaluation")
            return Response(res, content_type="application/json")
        instance.delete()
        return Response({"result": "StudentEvaluation instance was successfuly deleted!"})
