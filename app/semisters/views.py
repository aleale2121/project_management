from constants.constants import MODEL_ALREADY_EXIST, MODEL_PARAM_MISSED, MODEL_RECORD_NOT_FOUND
from core.models import Semister
from django.db import transaction
from pkg.util import error_response, success_response
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .serializer import SemisterSerializer
class SemisterViewSet(viewsets.ModelViewSet):
    serializer_class = SemisterSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["name"]
    search_fields = ["name"]
    filter_fields = ["name"]

    def get_queryset(self):
        queryset = Semister.objects.all()
        return queryset
    def retrieve(self, request, pk=None):
        if not pk.isdigit():
            res = error_response(request, MODEL_PARAM_MISSED, "Semister")
            res['message']='Invalid request parameter found.'
            return Response(res,status=int(res['status_code']), content_type="application/json")
        try:
            queryset = Semister.objects.get(pk=pk)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "Semister")
            res['message']='Semister not found with id '+pk+"."
            return Response(res,status=int(res['status_code']), content_type="application/json")
        serializer=SemisterSerializer(queryset)
        return Response(serializer.data)


    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("creating ...")
        data = request.data
        count = Semister.objects.filter(name=data["name"]).count()
        print("Count ", count)
        if count > 0:
            res = error_response(request, MODEL_ALREADY_EXIST, "Semister")
            return Response(res,status=int(res['status_code']), content_type="application/json")
        else:
            pass
        semister_obj = Semister.objects.create(name=data["name"])
        serializer = SemisterSerializer(semister_obj)
        data = success_response(serializer.data)
        return Response((data))
    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = Semister.objects.filter(name=str(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "Semister")
            return Response(res, status=int(res['status_code']),content_type="application/json")
        instance.delete()
        return Response({"result": "Semister instance was successfuly deleted!"})
