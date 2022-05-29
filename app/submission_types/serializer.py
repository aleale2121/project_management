from core.models import Semister, SubmissionType
from rest_framework import serializers


class SubmissionTypeSerializer(serializers.ModelSerializer):
    semister = serializers.PrimaryKeyRelatedField(queryset=Semister.objects.all())
    class Meta:
        model = SubmissionType
        fields = ["name","max_mark","semister"]