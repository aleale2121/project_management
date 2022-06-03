import json,pytz
from core.permissions import IsCoordinatorOrReadOnly
from datetime import datetime    
from constants.constants import MODEL_ALREADY_EXIST, MODEL_RECORD_NOT_FOUND
from core.models import Batch, Examiner, Member, StudentEvaluation, SubmissionDeadLine, SubmissionType, TitleDeadline
from django.db import transaction
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from pkg.util import error_response, success_response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .serializer import SubmissionDeadLineSerializer, TitleSubmissionDeadLineSerializer


class SubmissionDeadLineViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionDeadLineSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["name", "batch", "dead_line"]
    search_fields = ["name", "batch", "dead_line"]
    filter_fields = ["name", "batch", "dead_line"]
    # permission_classes=[IsCoordinatorOrReadOnly]
    __UTC = pytz.utc
    __current_date=datetime.now(__UTC)

    def get_queryset(self):
        deadlines = SubmissionDeadLine.objects.all().order_by("id")
        return deadlines

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
        date_form_data   = None
        new_sub_dead_line_obj = None
        if data["dead_line"]:
            date_form_data=datetime.strptime(data["dead_line"], "%Y-%m-%d %H:%M:%S")
            date_form_data = pytz.utc.localize(date_form_data)
            
        print("curent date =>",self.__current_date)            
        print("dat form data =>",date_form_data)            
        if date_form_data >= self.__current_date:
            try:
                new_sub_dead_line_obj = SubmissionDeadLine.objects.create(
                name=submission_type_obj, batch=batch_obj, dead_line=date_form_data
                )
            except:
                res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "SubmissionDeadline")
                res["message"]="Unable to set " +data["name"]+" deadline,try again." 
                return Response(res, content_type="application/json")
                
        else:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "SubmissionDeadline")
            res["message"]="Please try to set meaningful date form data." 
            return Response(res, content_type="application/json")
                

        serializer = SubmissionDeadLineSerializer(new_sub_dead_line_obj)
        data = success_response(serializer.data)
        return Response((data))

    def update(self, request, *args, **kwargs):
        print("updating ...")
        data = request.data
        pk = kwargs["pk"]
        if pk:
            pk = int(pk)
        sub_dead_line_obj =None
        try:
            sub_dead_line_obj =  SubmissionDeadLine.objects.get(pk=pk)
        except:
            res = error_response(request, MODEL_RECORD_NOT_FOUND, "SubmissionDeadLine")
            return Response(res, content_type="application/json")

        if data.get("name"):
            sub_dead_line_obj.name = data["name"]
        else:
            pass

        if data.get("batch"):
            sub_dead_line_obj.batch = data["batch"]
        else:
            pass

        if data.get("dead_line"):
            sub_dead_line_obj.dead_line = data["dead_line"]
        else:
            pass

        sub_dead_line_obj.save()
        print("updated.")
        serializer = SubmissionDeadLineSerializer(sub_dead_line_obj)
        return Response(serializer.data)
    
    @action(
        detail=False,
        methods=["GET"],
        url_path="check",
    )
    def get_deadline(self, request):
        print("get deadline line  1002")
        sub= request.GET.get('sub')
        dead_line_obj=None
        if sub is not None:
            batch_obj=None
            try:
                batch_obj=Batch.objects.get(is_active=True)
            except:
                res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "Batch")
                res["message"]="No active batch found!"
                return Response(res, content_type="application/json")
            
            try:
                dead_line_obj=SubmissionDeadLine.objects.get(name=sub,batch=batch_obj)
            except:
                res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "SubmissionDeadLine")
                res["message"]=f"SubmissionDeadLine does not exist with submission type {sub}!"
                return Response(res, content_type="application/json")
            
            deadline=dead_line_obj.dead_line
            print("deadline =>",deadline,"current_date=>",self.__current_date)
            if deadline >= self.__current_date:
                dead_line_obj.status=True
        serializer=SubmissionDeadLineSerializer(dead_line_obj)
        return Response(serializer.data)
         

    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = SubmissionDeadLine.objects.filter(id=int(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "SubmissionDeadLine")
            return Response(res, content_type="application/json")
        instance.delete()
        return Response({"result": "SubmissionDeadLine instance was successfuly deleted!"})






class TitleSubmissionDeadLineViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSubmissionDeadLineSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["batch"]
    permission_classes=[IsCoordinatorOrReadOnly]
    queryset = TitleDeadline.objects.all()