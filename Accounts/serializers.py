from rest_framework import serializers
from .models import *
from payment.models import *
from datetime import datetime



class UserPostNatalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'firstname', 'lastname', 'mobile', 'fcm_token','password')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CustomerDetailsSerializer(serializers.ModelSerializer):
    # Add a new field for first name, and use 'source' to point to the related User's first name
    first_name = serializers.CharField(source='user.firstname', read_only=True)

    class Meta:
        model = CustomerDetails
        fields = ['id', 'address', 'date_of_birth_parent', 'babydob', 'profile_img', 'babyGender', 'user', 'doctor_referal', 'first_name']




from rest_framework.validators import UniqueValidator

class DoctorRegistrationSerializer(serializers.Serializer):
    # User registration fields
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    firstname = serializers.CharField(max_length=100, required=True)
    lastname = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    # Doctor-specific fields
    speciality = serializers.CharField(max_length=200, required=True)
    qualification = serializers.CharField(max_length=200, required=True)
    medicalCouncil = serializers.CharField(max_length=20, required=True)
    councilRegNo = serializers.CharField(max_length=200, required=True)
    hospitals = serializers.CharField(max_length=300, required=True)
    interests = serializers.CharField(max_length=200, required=True)
    placeOfWork = serializers.CharField(max_length=200, required=True)
    onlineConsultation = serializers.CharField(max_length=100, required=True)
    experience = serializers.IntegerField(required=True)
    age = serializers.IntegerField(required=True)
    languages = serializers.CharField(max_length=500, required=False)
    location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    referalId = serializers.CharField(max_length=100, required=False, allow_blank=True)
    price = serializers.IntegerField(required=False)
    gender = serializers.ChoiceField(choices=DoctorDetails.GENDER_CHOICES, required=False, allow_blank=True)


class SalesTeamRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    firstname = serializers.CharField()
    lastname = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField()

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        firstname = validated_data['firstname']
        lastname = validated_data.get('lastname', '')
        location = validated_data['location']

        # Create the user with the SALES role
        user = User.objects.create_user(email=email, password=password, role=4, firstname=firstname, lastname=lastname)

        # Create SalesTeamDetails
        SalesTeamDetails.objects.create(user=user, location=location)

        return user
    

class ConsultantTeamRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    firstname = serializers.CharField()
    lastname = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField()

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        firstname = validated_data['firstname']
        lastname = validated_data.get('lastname', '')
        location = validated_data['location']

        # Create the user with the CONSULTANT role
        user = User.objects.create_user(email=email, password=password, role='CONSULTANT', firstname=firstname, lastname=lastname)

        # Create ConsultantInfo
        ConsultantInfo.objects.create(user=user, location=location)

        return user


class DoctorDetailSerializer(serializers.ModelSerializer):
    accountStatus = serializers.BooleanField(source='user.is_active')
    
    

    # new
    id = serializers.CharField(source='user.id')
    firstname = serializers.CharField(source='user.firstname')
    lastname = serializers.CharField(source='user.lastname')
    email = serializers.CharField(source='user.email')
    



    class Meta:
        model = DoctorDetails
        fields = ['id' ,'firstname', 'hospitals','lastname', 'email', 'age', 'location', 'councilRegNo', 'experience','qualification','speciality', 'accountStatus', 'price', 'gender', 'languages', 'referalId',]


# admin serializers
from django.db.models import Prefetch
   

class totalClientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
    email = serializers.CharField(source='user.email')
    firstname = serializers.CharField(source='user.firstname')
    lastname = serializers.CharField(source='user.lastname')
    dateJoined = serializers.DateTimeField(source='user.dateJoined')
    subscription = serializers.SerializerMethodField()
  
    doctor_firstname = serializers.CharField(source='referalId.user.firstname', required=False)
    doctor_lastname = serializers.CharField(source='referalId.user.lastname', required=False)
    is_active = serializers.BooleanField(source='user.is_active')
   
    profile_pic = serializers.ImageField(source="user.profile_img")
    
    class Meta:
        model = CustomerDetails
        fields = ['id', 'firstname', 'lastname', 'email', 'dateJoined', 'doctor_firstname', 'doctor_lastname', 'is_active','subscription', 'profile_pic']

    

    

    def get_subscription(self, obj):
        membership = PurchasedMembership.objects.filter(user = obj.user,is_paid = True).order_by('-pk')


        if membership.exists():
            return membership[0].membership.membership_name
        
                   
        return "No plans"
        


    @staticmethod
    def pre_loader(queryset):
        queryset = queryset.prefetch_related(
            'user',
            'doctor_referal',
          
            Prefetch("user__sub_client", queryset=Subscriptions.objects.filter(is_active=True).prefetch_related('membership'))
        )
        return queryset
    
class adminDashboardCountsSerializer(serializers.Serializer):
    totalConsultant = serializers.IntegerField()
    totalSalesTeam = serializers.IntegerField()
    activeClients = serializers.IntegerField()
    disabledDoctors = serializers.IntegerField()
    totalDoctors = serializers.IntegerField()
    totalClients = serializers.IntegerField()

