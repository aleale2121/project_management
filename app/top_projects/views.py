from core.models import TopProject
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import TopProjectSerializer


# TopProject views.
@api_view(["GET"])
def GetAllTopProject(request):
    top_projects = TopProject.objects.all()
    serializer = TopProjectSerializer(top_projects, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def GetTopProjectByID(request, pk):
    top_project = TopProject.objects.get(user_id=pk)
    serializer = TopProjectSerializer(top_project, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def CreateTopProject(request):
    serializer = TopProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(["PUT"])
def UpdateTopProject(request, pk):
    top_project = TopProject.objects.get(pk)
    serializer = TopProjectSerializer(instance=top_project, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(["DELETE"])
def DeleteTopProject(request, pk):
    top_project = TopProject.objects.get(pk)
    top_project.delete()
    return Response("TopProject Deleted!")

