from core.models import TopProject
from rest_framework import serializers


class TopProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopProject
        fields = ["id", "title_name", "level"]
