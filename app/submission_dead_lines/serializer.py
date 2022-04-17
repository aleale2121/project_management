from os import defpath

from core.models import SubmissionDeadLine
from rest_framework import serializers


class SubmissionDeadLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionDeadLine
        fields = ["name", "batch", "dead_line"]
        depth = 1
