from constants.constants import MODEL_ALREADY_EXIST, MODEL_PARAM_MISSED, MODEL_RECORD_NOT_FOUND
from core.models import NumberOfVoter, TopProject
from django.db import transaction
from pkg.util import error_response, success_response
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .serializer import NumberOfVoterSerializer
class NumberOfVoterViewSet(viewsets.ModelViewSet):
    serializer_class = NumberOfVoterSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["id","project"]
    search_fields = ["id","project"]
    filter_fields = ["id","project"]

    def get_queryset(self):
        queryset = NumberOfVoter.objects.all().order_by("id")
        return queryset
    def retrieve(self, request, pk=None):
        if not pk.isdigit():
            res = error_response(request, MODEL_PARAM_MISSED, "NumberOfVoter")
            res['message']='Invalid request parameter found.'
            return Response(res,status=int(res['status_code']), content_type="application/json")
        try:
            queryset = NumberOfVoter.objects.get(pk=pk)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "NumberOfVoter")
            res['message']='NumberOfVoter not found with id '+pk+"."
            return Response(res,status=int(res['status_code']), content_type="application/json")
        serializer=NumberOfVoterSerializer(queryset)
        return Response(serializer.data)


    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("creating ...")
        data = request.data
        project_id=0
        project_obj=None
        if data["project"]:
            project_id =int(data["project"])
        try:
            NumberOfVoter.objects.filter(project=project_id).exists()
        except:
            res = error_response(request, MODEL_ALREADY_EXIST, "NumberOfVoter")
            res['message']='No more project statics registrations'
            return Response(res,status=int(res['status_code']), content_type="application/json")
        else:
            pass
        
        try:
            project_obj= TopProject.objects.get(id=project_id)[0]
        except:
            res = error_response(request, MODEL_ALREADY_EXIST, "TopProject")
            res['message']=f"TopProject not found with id of {project_id}"
            return Response(res,status=int(res['status_code']), content_type="application/json")
          
        semister_obj = NumberOfVoter.objects.create(project=project_obj)
        data = NumberOfVoterSerializer(semister_obj).data
        return Response(data)
    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = NumberOfVoter.objects.filter(id=str(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "NumberOfVoter")
            res['message']='Unable to delete.'
            return Response(res, status=int(res['status_code']),content_type="application/json")
        instance.delete()
        return Response({"result": "NumberOfVoter instance was successfuly deleted!"})
