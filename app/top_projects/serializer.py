from os import defpath
from numberofprojects.serializer import NumberOfVoterSerializer

from core.models import TopProject, Voter,NumberOfVoter
from rest_framework import serializers
class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        ordering = ['id']
        fields =  '__all__'
        depth = 2
class TopProjectSerializer(serializers.ModelSerializer):
    no_voters = NumberOfVoterSerializer(many=True)
    class Meta:
        model = TopProject
        ordering = ['id']
        fields = '__all__'
        depth = 2


