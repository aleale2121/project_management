from os import defpath

from core.models import Batch, SubmissionDeadLine, TitleDeadline
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class SubmissionDeadLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionDeadLine
        fields = ["id", "name", "batch", "dead_line"]
        depth = 1


class TitleSubmissionDeadLineSerializer(serializers.ModelSerializer):
    batch = serializers.SlugField(
        validators=[UniqueValidator(queryset=TitleDeadline.objects.all())]
    )
    deadline=serializers.DateTimeField()
    class Meta:
        model = TitleDeadline
        fields = ["id", "batch", "deadline"]
        depth = 1
