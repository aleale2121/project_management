from constants.constants import MODEL_ALREADY_EXIST, MODEL_CREATION_FAILED, MODEL_RECORD_NOT_FOUND
from core.models import Mark
from django.db import transaction
from pkg.util import error_response, success_response
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .serializer import MarkSerializer
class MarkViewSet(viewsets.ModelViewSet):
    serializer_class = MarkSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["id"]
    search_fields = ["id"]
    filter_fields = ["id"]

    def get_queryset(self):
        queryset = Mark.objects.all()
        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        res = error_response(self.request, MODEL_CREATION_FAILED, "Mark")
        res['message']='Unable to add mark!'
        return Response(res, status=int(res['status_code']), content_type="application/json")
        
    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = Mark.objects.filter(name=str(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "Semister")
            return Response(res, status=int(res['status_code']),content_type="application/json")
        instance.delete()
        return Response({"result": "Semister instance was successfuly deleted!"})
