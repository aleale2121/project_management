from os import defpath

from core.models import TopProject, Voter
from rest_framework import serializers


class TopProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopProject
        ordering = ['id']

        fields = ["id","title","group", "batch", "doc_path","vote","description","is_approved"]
        depth = 1
class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        ordering = ['id']

        fields = ["user_id","project_id"]
        depth = 1
