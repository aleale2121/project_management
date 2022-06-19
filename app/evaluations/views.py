import json
from urllib.request import proxy_bypass

from constants.constants import FORBIDDEN_REQUEST_FOUND, MODEL_ALREADY_EXIST, MODEL_CREATION_FAILED, MODEL_RECORD_NOT_FOUND
from core.models import Batch, Evaluation, Examiner, Group, Mark, Member, StudentEvaluation, SubmissionType,User
from django.db import transaction
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from pkg.util import error_response, success_response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from core.permissions import IsAdmin, IsStudent
from django.db.models import  Sum
# from django.core import serializers

from .serializer import EvaluationSerializer, ReadStudentSerializer, StudentEvaluationSerializer


class EvaluationFilter(filters.FilterSet):
    student = filters.NumberFilter(field_name="member")
    assesment = filters.CharFilter(field_name="submission_type")
    examiner = filters.NumberFilter(field_name="examiner")
    group = filters.NumberFilter(field_name="group")
    group_name = filters.CharFilter(field_name="member__group__group_name")
    student_id = filters.NumberFilter(field_name="member__member__id")
    student_username = filters.NumberFilter(field_name="member__member__username")
    examiner_id = filters.NumberFilter(field_name="examiner__examiner")
    examiner_username = filters.NumberFilter(field_name="examiner__examiner__username")
    batch = filters.CharFilter(field_name="batch")

    class Meta:
        model = Evaluation
        fields = ["group","batch", "submission_type", "examiner","marks"]


class EvaluaionViewSet(viewsets.ModelViewSet):
    serializer_class = EvaluationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_class = EvaluationFilter
    ordering_fields = ["examiner", "submission_type"]
    search_fields = ["examiner", "submission_type", "member"]
    filterset_fields = [
        "batch","group","id"
    ]
    def get_queryset(self):
        print("fetching ...")
        queryset = Evaluation.objects.all()
        # serializer = ReadStudentSerializer(queryset, many=True)
        return queryset
    
    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsStudent],
        url_path="(?P<batch>[^/.]+)/(?P<group>[^/.]+)/(?P<id>[^/.]+)",
    )
    def getComment(self, request,batch,group,id):
        comment=None
        count=Evaluation.objects.filter(group=group,batch=batch,marks__member=id).count()
        if (count==4):
            comment=Evaluation.objects.filter(group=group,batch=batch,marks__member=id).values("member_id","submission_type_id","comment","mark")
        else:  
            comment=Evaluation.objects.filter(group=group,batch=batch,marks__member=id).values("submission_type","comment")
        return Response(comment)



    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("creating ...")
        evaluation_data = request.data
        submission_type_obj=None
        member_obj=None
        examiner_obj=None
        evaluation_obj=None
        group_obj=None
        batch_obj=None
        print("evaluation_data =>",evaluation_data)
        try:
            batch_obj = Batch.objects.get(name=evaluation_data["batch"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Batch")
            res['message']="Group batch is not found"
            return Response(res,status=int(res['status_code']), content_type="application/json")
        
        try:
            group_obj = Group.objects.get(id=evaluation_data["group"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Group")
            res['message']="Group is not found"
            return Response(res,status=int(res['status_code']), content_type="application/json")
        
        
        try:
            submission_type_obj = SubmissionType.objects.get(name=evaluation_data["submission_type"])
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "SubmissionType")
            return Response(res, status=int(res['status_code']),content_type="application/json")
        
        
        id=self.request.user.id
        user=None
        examiner_obj=None
        print("ID ",id )
        if id:
            try:
                user=User.objects.get(id=id)
                print(" username ",user.username," id ",user.id)
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "Examiner")
                res["message"]="Examiner not found."
                return Response(res, status=int(res['status_code']),content_type="application/json")
        try: 
            examiner_obj = Examiner.objects.get(examiner=user)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Examiner")
            res["message"]=" User is not an examiner"
            return Response(res,status=int(res['status_code']), content_type="application/json")
        is_exist=False
        is_exist = Evaluation.objects.filter(
            submission_type=submission_type_obj,
            examiner=examiner_obj, 
            group=group_obj,
            batch=batch_obj
        ).exists()
        print("=== is exist ==== ",is_exist)

        if is_exist:
            print("line ===131")
            res = error_response(request, MODEL_ALREADY_EXIST, "StudentEvaluation")
            res['message']="student can't be evaluated multiple times for the same submission type."
            return Response(res, status=int(res['status_code']),content_type="application/json")
        else:
            pass
        
        
        print(evaluation_data['group']," <=> ",examiner_obj.group.id)
        if(int(evaluation_data['group'])!=int(examiner_obj.group.id)):
            res = error_response(request, MODEL_CREATION_FAILED, "Examiner")
            res['message']="You don't have permission to evaluate this group."
            return Response(res, status=int(res['status_code']),content_type="application/json")
      
      
        evaluation_obj=Evaluation(
            submission_type=submission_type_obj,
            group=group_obj,
            batch=batch_obj,
            examiner=examiner_obj,
            comment=evaluation_data["comment"])
        
        
        for data in evaluation_data['students_mark']:
            print("=======================================")
            try:
                member_obj = User.objects.get(username=data["member"])
            except:
                res = error_response(request, MODEL_RECORD_NOT_FOUND, "User")
                res['message']='Student record not found'
                return Response(res, status=int(res['status_code']),content_type="application/json")
            print("submission_type_obj.max_mark ",type(submission_type_obj.max_mark))
            print("data['mark'] ",type(data["mark"]))
            
            if (float(data["mark"])>=0 and float(data["mark"])<=submission_type_obj.max_mark):
                pass
            else:
                res = error_response(request, FORBIDDEN_REQUEST_FOUND, "StudentEvalaution")
                res["message"]='please enter mark which is between 0 and '+str(submission_type_obj.max_mark)
                return Response(res, status=int(res['status_code']),content_type="application/json")
            mark_obj=Mark.objects.create(member=member_obj,mark=data['mark'])
            evaluation_obj.save()
            evaluation_obj.marks.add(mark_obj)
        
        serializer = EvaluationSerializer(evaluation_obj)
        data = serializer.data
        return Response(data)

    def update(self, request, *args, **kwargs):
        print("updating ...")
        data = request.data
        print(type(data))
        pk = kwargs["pk"]
        evaluation_obj=None
        if pk:
            pk = int(pk)
        try:
            evaluation_obj = Evaluation.objects.get(pk=pk)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "StudentEvaluation")
            res['message']="Evaluation record not found"
            return Response(res, status=int(res['status_code']),content_type="application/json")
        submission_type_obj=None
        try:
            submission_type_obj = SubmissionType.objects.get(name=evaluation_obj.submission_type)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "SubmissionType")
            res['message']="Submission Type is not  found"
            return Response(res, status=int(res['status_code']),content_type="application/json")
        if data.get("comment"):
            evaluation_obj.comment = data["comment"]
        else:
            pass
        if (float(data["mark"])>=0 and float(data["mark"])<=submission_type_obj.max_mark):
            pass
        else:
            res = error_response(request, FORBIDDEN_REQUEST_FOUND, "StudentEvalaution")
            res['message']="You don't have permission to evaluate this group."
            return Response(res, status=int(res['status_code']),content_type="application/json")
        if data.get("mark"):
            evaluation_obj.mark = float(data["mark"])
        else:
            pass
        evaluation_obj.save()
        print("updated.")
        serializer = StudentEvaluationSerializer(evaluation_obj)
        return Response(serializer.data,status=int(res['status_code']))

    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = Evaluation.objects.filter(id=int(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "StudentEvaluation")
            return Response(res, status=int(res['status_code']),content_type="application/json")
        instance.delete()
        return Response({"result": "StudentEvaluation instance was successfuly deleted!"},status=status.HTTP_204_NO_CONTENT)
