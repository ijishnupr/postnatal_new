from Accounts.models import *
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site

User = get_user_model()




class AddMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicines
        fields = '__all__'

class TakenMedicineSerializer(serializers.ModelSerializer):
    medicine = serializers.CharField(source='medicine.name') 
    medicationTime = serializers.CharField(source='medicine.time.name') 
    class Meta:
        # list_serializer_class = MedicineFilter
        model = TakenMedicine
        fields = '__all__'
        extra_kwargs = {
            'customer' : {'write_only' : True},
        }
    def to_representation(self, instance):
        representation = super(TakenMedicineSerializer, self).to_representation(instance)
        representation['date'] = instance.date.strftime("%d-%m-%Y")
        return representation
    
class MedicineSerializer(serializers.ModelSerializer):
    taken = serializers.SerializerMethodField()
    MedicationTime = serializers.CharField(source="time.name")
    class Meta:
        model = Medicines
        fields = ['id', 'name', 'taken', 'MedicationTime']
        extra_kwargs = {
            'customer' : {'write_only' : True},
            'time' : {'write_only' : True},
            'taken' : {'read_only' : True},
            'MedicationTime' : {'read_only' : True}
        }
        
    def get_taken(self,obj):
        response = obj.MedicineDetail.first()
        # print(len(connection.queries))
        try:
            return response.taken 
        except:
            return False
        
class MedicineTimeSerializer(serializers.ModelSerializer):
    Medicines = MedicineSerializer(many=True)
    MedicationTime = serializers.CharField(source="name")
    class Meta:
        # print(len(connection.queries))
        model = MedicineTime
        fields = ['MedicationTime', 'Medicines']
    

class BreastfeedingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreastfeedingRecord
        fields = ['feeding_number', 'is_breastfed']

class UserBreastfeedingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBreastfeedingRecord
        fields = ['user', 'breastfeeding_record', 'date', 'is_breastfed']

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model=Exercise
        fields='__all__'

class Calserializer(serializers.ModelSerializer):
    class Meta:
        model=CaloriesBurnt
        fields=['value']


#diet serialzer
class DietTrackerSerializer(serializers.ModelSerializer):
    mealType = serializers.CharField(read_only=True)
    mealName = serializers.CharField(source='meal.name', required=False)
    # customerName = serializers.CharField(source='customer.firstname', required=False)
    class Meta:
        model = DietTracker
        fields = '__all__'
        extra_kwargs = {
            'meal' : {'write_only' : True},
            'customer' : {'write_only' : True},
        }

class mealSerialzer(serializers.ModelSerializer):
    class Meta:
        model=Meal
        fields='__all__'


class Vaccineserializer(serializers.ModelSerializer):
    name=serializers.CharField(source='Vaccinations.name',read_only=True)
    age=serializers.CharField(source='Vaccinations.age',read_only=True)
    agent=serializers.CharField(source='Vaccinations.against',read_only=True)

    class Meta:
        model=Vaccination_user
        fields = ('id', 'user', 'status', 'name','age','agent', 'date')

class Brainuserserializer(serializers.ModelSerializer):
    class Meta:
        model=Brain_sense_user
        fields='__all__'