from rest_framework import serializers
from Accounts.models import CustomerDetails
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from Accounts.models import *
from datetime import timedelta, datetime
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'firstname', 'lastname']  # Include any other user fields me want

class CustomerDetailsSerializer(serializers.ModelSerializer):
    referalId = serializers.SerializerMethodField()
    user = UserSerializer()
    class Meta:
        model = CustomerDetails
        fields = ['user', 'address', 'date_of_birth_parent', 'babydob', 'profile_img', 'babyGender', 'referalId']


    def get_referalId(self, obj):
        # Retrieve the referalId from the associated DoctorDetails
        return obj.doctor_referal.referalId if obj.doctor_referal else None
    
class GraphDataSerializer(serializers.Serializer):
    month = serializers.DateField(format='%B')
    appointments = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    # month = serializers.SerializerMethodField()

    # def get_month(self, obj)

    
class DoctorProfileSerialzer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    firstname = serializers.CharField(source='user.firstname')
    lastname = serializers.CharField(source='user.lastname')
    email = serializers.EmailField(source='user.email')
    mobile = serializers.CharField(source='user.mobile')
    profile_full_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta: 
        model = DoctorDetails
        fields = '__all__'
        
    def get_profile_full_url(self, obj):
        request = self.context.get('request')
        try:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.user.profile_img)
        except:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")
        
class MyPatientSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    dueDate = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    accountStatus = serializers.BooleanField(source='user.is_active')
    currentWeek = serializers.SerializerMethodField()
    days = serializers.SerializerMethodField()
    firstname = serializers.CharField(source="user.firstname")
    lastname = serializers.CharField(source="user.lastname")
    profile_pic = serializers.SerializerMethodField()
    dateJoined = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerDetails
        fields = ['id', 'firstname', 'lastname', 'age', 'location', 'dueDate', 'accountStatus', 'currentWeek', 'days', 'profile_pic','dateJoined']
    
    def get_dateJoined(self, obj):
        # Assuming 'dateJoined' is a datetime field, you can format it as follows
        return obj.user.dateJoined.strftime('%Y-%m-%d')

    def get_profile_pic(self,obj):
        request = self.context.get('request')
        if obj.user.profile_img:
            return "https://" + str(get_current_site(request)) + "/media/" + str(obj.user.profile_img)
        else:
            return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")
            
    def get_location(self, obj):
        # instance = obj.customer_details.first()
        return obj.location

    def get_age(self, obj):
        # instance = obj.customer_details.first()
        return obj.age


