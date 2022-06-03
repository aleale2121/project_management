from os import defpath

from core.models import Batch, SubmissionDeadLine, TitleDeadline
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.fields import SerializerMethodField
from django.utils import timezone


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
    status = SerializerMethodField()
    class Meta:
        model = TitleDeadline
        fields = ["id", "batch", "deadline","status"]
        depth = 1
    def get_status(self, obj):
        current_time = timezone.now()
        return obj.deadline > current_time
