import json
from urllib.request import proxy_bypass

from constants.constants import FORBIDDEN_REQUEST_FOUND, MODEL_ALREADY_EXIST, MODEL_CREATION_FAILED, MODEL_RECORD_NOT_FOUND
from core.models import Examiner, Member, StudentEvaluation, SubmissionType,User
from django.db import transaction
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from pkg.util import error_response, success_response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from core.permissions import IsAdmin, IsExaminer, IsStudent
from django.db.models import  Sum
# from django.core import serializers

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
    permission_classes=[IsExaminer]
    serializer_class = StudentEvaluationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_class = StudentEvaluationFilter
    ordering_fields = ["examiner", "submission_type", "member"]
    search_fields = ["examiner", "submission_type", "member"]
    filterset_fields = [
        "batch","group","id"
    ]
    queryset=None
    def get_queryset(self):
        print("fetching ...")
        queryset = StudentEvaluation.objects.all()
        return queryset
    
    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsStudent],
        url_path="(?P<batch>[^/.]+)/(?P<group>[^/.]+)/(?P<id>[^/.]+)",
    )
    def getComment(self, request,batch,group,id):
        comment=None
        count=StudentEvaluation.objects.filter(member__group=group,member__group__batch=batch,member__member=id).count()
        if (count==4):
            comment=StudentEvaluation.objects.filter(member__group=group,member__group__batch=batch,member__member=id).values("member_id","submission_type_id","comment","mark")
        else:  
            comment=StudentEvaluation.objects.filter(member__group=group,member__group__batch=batch,member__member=id).values("submission_type","comment")
        return Response(comment)



    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("creating ...")
        evaluation_data = request.data
        global submission_type_obj
        global member_obj
        global examiner_obj
        global new_student_obj
        
        
        try:
            submission_type_obj = SubmissionType.objects.get(name=evaluation_data["submission_type"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "SubmissionType")
            return Response(res, content_type="application/json")
        try:
            usr=self.request.user
            user=User.objects.get(username=usr)
            examiner_obj = Examiner.objects.get(examiner=user)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Examiner")
            return Response(res, content_type="application/json")
        print("=======================================")
        
        for data in evaluation_data['students_mark']:
            global student_obj
            print("=======================================")
            try:
                member_obj = Member.objects.get(id=data["member"])
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "Member")
                return Response(res, content_type="application/json")
            if (data["mark"]>=0 and data["mark"]<=submission_type_obj.max_mark):
                pass
            else:
                res = error_response(request, FORBIDDEN_REQUEST_FOUND, "StudentEvalaution")
                return Response(res, content_type="application/json")

            count = StudentEvaluation.objects.filter(
                submission_type=submission_type_obj,
                 examiner=examiner_obj, 
                 member=member_obj
            ).count()

            if count > 0:
                res = error_response(request, MODEL_ALREADY_EXIST, "StudentEvaluation")
                return Response(res, content_type="application/json")
            else:
                pass
            # print(member_obj.group.id," <=> ",examiner_obj.group.id)
            if(member_obj.group.id!=examiner_obj.group.id):
                res = error_response(request, MODEL_CREATION_FAILED, "Examiner")
                return Response(res, content_type="application/json")
            
            
            
            new_student_obj = StudentEvaluation.objects.create(
                submission_type=submission_type_obj,
                examiner=examiner_obj,
                member=member_obj,
                mark=data["mark"],
                comment=evaluation_data["comment"],
            )
            
        serializer = StudentEvaluationSerializer(new_student_obj)
        data = success_response(serializer.data)
        return Response((data))

    def update(self, request, *args, **kwargs):
        print("updating ...")
        data = request.data
        print(type(data))
        pk = kwargs["pk"]
        global student_result
        if pk:
            pk = int(pk)
        try:
            student_result = StudentEvaluation.objects.get(pk=pk)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "StudentEvaluation")
            return Response(res, content_type="application/json")

        if data.get("comment"):
            student_result.comment = data["comment"]
        else:
            pass
        if (data["mark"]>=0 and data["mark"]<=submission_type_obj.max_mark):
            pass
        else:
            res = error_response(request, FORBIDDEN_REQUEST_FOUND, "StudentEvalaution")
            return Response(res, content_type="application/json")
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
