from core.models import Submission
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

class SubmissionsSerializer(serializers.ModelSerializer):
    batch = SerializerMethodField()
    class Meta:
        model = Submission
        fields = "__all__"
    
    def get_batch(self, obj):
        return obj.group.batch.name
