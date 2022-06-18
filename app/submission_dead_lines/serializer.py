from os import defpath

from core.models import Batch, SubmissionDeadLine, TitleDeadline
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class SubmissionDeadLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionDeadLine
        fields = ["id", "name", "batch", "dead_line","status"]
        depth = 1


class TitleSubmissionDeadLineSerializer(serializers.ModelSerializer):
    batch = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Batch.objects.all(),
        validators=[UniqueValidator(queryset=TitleDeadline.objects.all())]
    )
    deadline=serializers.DateTimeField()
    class Meta:
        model = TitleDeadline
        fields = ["id", "batch", "deadline"]
        depth = 1


