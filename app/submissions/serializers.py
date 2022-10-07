import os
from tokenize import group
from core.models import ProjectTitle, Submission
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

class SubmissionsSerializer(serializers.ModelSerializer):
    batch = SerializerMethodField()
    filename = SerializerMethodField()
    title=SerializerMethodField()
    class Meta:
        model = Submission
        fields = "__all__"
    
    def get_batch(self, obj):
        return obj.group.batch.name
    def get_filename(self, obj):
        return os.path.basename(obj.file.name)
    def get_title(self, obj):
        pr_title=""
        try:
            t=ProjectTitle.objects.get(group=obj.group,status="APPROVED")
            pr_title=t.title_name
            pass
        except ProjectTitle.DoesNotExist :
            pass
        return pr_title
