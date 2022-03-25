from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from core.models import Group
from groups.serializers import GroupSerializer
from core.permissions import IsAdmin, IsAdminOrReadOnly, IsStaff, IsStudent


class GroupsModelViewSet(ModelViewSet):
    queryset = Group.objects.all()

    permission_classes = [IsAdmin]
    serializer_class = GroupSerializer

    