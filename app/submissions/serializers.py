from core.models import Submission
from rest_framework import serializers

class SubmissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"