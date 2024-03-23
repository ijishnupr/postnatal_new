from rest_framework import serializers
from .models import *


class Membership2Serializer(serializers.ModelSerializer):
    
    class Meta:
        model = MemberShip
        fields = '__all__'
