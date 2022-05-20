from core.models import Semister
from rest_framework import serializers


class SemisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semister
        fields = ["id","name"]