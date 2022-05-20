from core.models import SubmissionType
from rest_framework import serializers


class SubmissionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionType
        fields = ["name","max_mark","semister"]