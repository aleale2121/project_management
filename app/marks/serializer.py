from core.models import Mark
from rest_framework import serializers


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = ["id","member","mark"]