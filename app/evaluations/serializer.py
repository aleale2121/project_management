from core.models import StudentEvaluation
from rest_framework import serializers


class StudentEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEvaluation
        fields = ["member", "submission_type", "examiner", "comment", "mark"]
        extra_kwargs = {"created_at": {"write_only": True}, "updated_at": {"write_only": True}}
        depth = 3
