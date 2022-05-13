from constants.constants import MODEL_ALREADY_EXIST, MODEL_RECORD_NOT_FOUND
from core.models import ProjectTitle
from django.db import transaction
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from pkg.util import error_response, success_response
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from .serializer import TitleSerializer


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ["name"]
    search_fields = ["name"]
    filter_fields = ["name"]

    def get_queryset(self):
        titles = ProjectTitle.objects.all()
        return titles

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("creating ...")
        data = request.data
        count = ProjectTitle.objects.filter(name=data["name"]).count()
        print("Count ", count)
        if count > 0:
            res = error_response(request, MODEL_ALREADY_EXIST, "Title")
            return Response(res, content_type="application/json")
        else:
            pass
        new_title_obj = ProjectTitle.objects.create(name=data["name"])
        serializer = TitleSerializer(new_title_obj)
        data = success_response(serializer.data)
        return Response((data))

    def update(self, request, *args, **kwargs):
        print("updating ...")
        data = request.data
        pk = kwargs["pk"]
        if pk:
            pk = str(pk)
        title = ProjectTitle.objects.get(name=pk)
        if data.get("name"):
            title.name = data["name"]
        else:
            pass
        title.save()
        print("updated.")
        serializer = TitleSerializer(title)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        print("deleting ...")
        instance = ProjectTitle.objects.filter(name=str(kwargs["pk"]))
        if len(instance) != 1:
            res = error_response(self.request, MODEL_RECORD_NOT_FOUND, "Title")
            return Response(res, content_type="application/json")
        instance.delete()
        return Response({"result": "Title instance was successfuly deleted!"})
