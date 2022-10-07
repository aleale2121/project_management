from core.models import NumberOfVoter
from rest_framework import serializers


class NumberOfVoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberOfVoter
        ordering = ['id']
        fields = ['id',"project","staffs","students"]
        
        
        