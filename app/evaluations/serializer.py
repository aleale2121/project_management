from users.serializers import UserSerializer
from core.models import Evaluation, Student, StudentEvaluation, User
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField


class StudentEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEvaluation
        fields ="__all__"
        extra_kwargs = {"created_at": {"write_only": True}, "updated_at": {"write_only": True}}
class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields ="__all__"
        extra_kwargs = {"created_at": {"write_only": True}, "updated_at": {"write_only": True}}
        read_only_field=('id')
        depth=2
    
    
class ReadStudentSerializer(serializers.ModelSerializer):
    username = SerializerMethodField()
    email = SerializerMethodField()

    class Meta:
        model = StudentEvaluation
        fields =  ["username",'email',"group", "batch","submission_type", "examiner", "comment", "marks"]

    def validate(self, data):
        return super().validate(data)

    def get_username(self, obj):

        return obj.member.member.username

    def get_email(self, obj):
        return obj.member.member.email

    def get_batch(self, obj):
        student = Student.objects.get(user=obj.member)
        return student.batch.name


