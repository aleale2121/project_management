from constants.constants import MODEL_ALREADY_EXIST, MODEL_PARAM_MISSED, MODEL_RECORD_NOT_FOUND
from core.models import Semister, SubmissionType
from django.db import transaction
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from pkg.util import error_response, success_response
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from .serializer import SubmissionTypeSerializer

class SubmissionTypeViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionTypeSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["name"]
    search_fields = ["name"]
    filter_fields = ["name"]

    def get_queryset(self):
        evaluations = SubmissionType.objects.all()
        return evaluations

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("creating ...")
        data = request.data
        if not data["name"].isalpha() :
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Mark")
            res["message"]="SubmissionType name must be a sequence of valid english charactors."
            return Response(res,status=int(res['status_code']), content_type="application/json")
        
        if not str(data["max_mark"]).isdigit() :
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Mark")
            res["message"]="Maximum mark for Submission type must be a number."
            return Response(res,status=int(res['status_code']), content_type="application/json")
        
        if float(data["max_mark"])< float(5) and float(data["max_mark"])>float(100):
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Mark")
            res["message"]="Offially alloted mark value for submission "+data["name"] + " is in the range of 5 and 100."
            return Response(res,status=int(res['status_code']), content_type="application/json")
        
        is_exists = SubmissionType.objects.filter(name=data["name"]).exists()
        if is_exists:
            res = error_response(request, MODEL_ALREADY_EXIST, "SubmissionType")
            return Response(res,status=int(res['status_code']), content_type="application/json")
        else:
            pass
        semister_obj=None
        try:
            semister_obj=Semister.objects.filter(id=data["semister"]).first()
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Semister")
            return Response(res, status=int(res['status_code']),content_type="application/json")
       
       
        new_sub_type_obj = SubmissionType.objects.create(name=data["name"],semister=semister_obj,max_mark=data["max_mark"])
        serializer = SubmissionTypeSerializer(new_sub_type_obj)
        data = success_response(serializer.data)
        return Response((data))

    def update(self, request, *args, **kwargs):
        print("updating ...")
        data = request.data
        pk = kwargs["pk"]
        if not str(pk).isdigit():
            res = error_response(request, MODEL_PARAM_MISSED, "SubmissionType")
            res['message']='Invalid request parameter found.'
            return Response(res,status=int(res['status_code']), content_type="application/json")
        if pk:
            pk = str(pk)
        sub__type=None
        try:
            sub__type = SubmissionType.objects.get(name=pk)
        except:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "SubmissionType")
            res['message']='SubmissionType is not found'
            return Response(res,status=int(res['status_code']), content_type="application/json")
        if data.get("max_mark") and float(data.get("max_mark") )!=float(0):
            sub__type.max_mark = data["max_mark"]
        else:
            pass
        if data.get("semister"):
            semister_obj=None
            try:
                semister_obj=Semister.objects.get(id= int(data["semister"]))
                sub__type.semister = semister_obj
            except:
                res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "Semister")
                return Response(res,status=int(res['status_code']), content_type="application/json")
        else:
            pass
        
        sub__type.save()
        serializer = SubmissionTypeSerializer(sub__type)
        return Response(serializer.data)
    def retrieve(self, request, pk=None):
        if not pk.isdigit():
            res = error_response(request, MODEL_PARAM_MISSED, "SubmissionType")
            res['message']='Invalid request parameter found.'
            return Response(res,status=int(res['status_code']), content_type="application/json")
        try:
            queryset = SubmissionType.objects.get(pk=pk)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "SubmissionType")
            res['message']='SubmissionType not found with id '+pk+"."
            return Response(res,status=int(res['status_code']), content_type="application/json")
        serializer=SubmissionTypeSerializer(queryset)
        return Response(serializer.data)


    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = SubmissionType.objects.filter(name=str(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "SubmissionType")
            return Response(res, status=int(res['status_code']),content_type="application/json")
        instance.delete()
        return Response({"result": "SubmissionType instance was successfuly deleted!"})