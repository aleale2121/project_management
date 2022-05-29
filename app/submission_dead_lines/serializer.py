from os import defpath

from core.models import SubmissionDeadLine, TitleSubmissionDeadline
from rest_framework import serializers


class SubmissionDeadLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionDeadLine
        fields = ["id","name", "batch", "dead_line"]
        depth = 1

class TitleSubmissionDeadLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = TitleSubmissionDeadline
        fields = [ "batch", "deadline"]
        depth = 1