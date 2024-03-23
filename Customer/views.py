from django.shortcuts import render
from multiprocessing import context
from os import stat
from django.db.models.query import Prefetch
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.timezone import make_aware
from datetime  import date, timedelta, datetime
import datetime
from .models import LastUpdateDate
from django.http import JsonResponse
# Create your views here.

from django.contrib.auth import get_user_model 

User = get_user_model()



def update_date(instance, module):
    current_date = datetime.datetime.now()
    timezone_aware_date = make_aware(current_date)
    customer = User.objects.filter(id=instance.customer.id).first()
    LastUpdate, created = LastUpdateDate.objects.get_or_create(customer=customer)

    instanceDate = instance.date
    if isinstance(instanceDate, str):
        instanceDate = instanceDate.replace('-','')
        instanceDate = datetime.datetime.strptime(instanceDate, '%Y%m%d').date()

    if module == 'diet' and instanceDate >= LastUpdate.diet.date():
        LastUpdate.diet = timezone_aware_date
    elif module == 'activity' and instanceDate >= LastUpdate.activity.date():
        LastUpdate.activity = timezone_aware_date
    elif module == 'medicine' and instanceDate >= LastUpdate.medicine.date():
        LastUpdate.medicine = timezone_aware_date
    elif module == 'symptom' and instanceDate >= LastUpdate.symptom.date():
        LastUpdate.symptom = timezone_aware_date
    
    else:
        # LastUpdate.contraction = timezone_aware_date
        pass
    LastUpdate.save()

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def medicine_get(request):
    user = request.user
    if not user.role == 'SALES':
        # from calender
        date = request.query_params.get('date', None)
        cid = user.id if user.role == 'CLIENT' else request.query_params.get('customer', None)
        
        if cid is None:
            return Response({"Error" : "Provide id in params as customer:id"}, status=status.HTTP_400_BAD_REQUEST)
        # if date == None:
        #     date = datetime.datetime.now()
        # else:
        #     date = datetime.datetime.strptime(date, '%Y-%m-%d')
        date = date if date is not None else datetime.datetime.now().date()
        data = MedicineTime.objects.all().prefetch_related(
            Prefetch('Medicines',queryset=Medicines.objects.filter(customer=cid, date__lte=date)),
            Prefetch('Medicines__MedicineDetail',queryset=TakenMedicine.objects.filter(date=date))
        )
        serializer = MedicineTimeSerializer(data, many=True)
        return Response(serializer.data)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    


@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def medicine_post(request):
    user = request.user
    
    if user:
        data = request.data.copy()
        if user:
            data['customer'] = user.id
        else:
            cid = request.data.get('customer', None)
            if cid is not None:
                try:
                    customer = User.objects.get(id=cid)
                    data['customer'] = customer.id
                except User.DoesNotExist:
                    
                    return Response({'error' : 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error' : 'provide customer in data'}, status=status.HTTP_400_BAD_REQUEST)

        medTime = request.data.get('medicationTime', None)
        if medTime is not None:
            try:
                med_time = MedicineTime.objects.get(name=medTime)
            except MedicineTime.DoesNotExist:
                return Response({"error" : "Medicine Time not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error" : "Medicine Time cannot be empty"})

        data['time'] = med_time.id
        serializer = AddMedicineSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            update_date(instance,"medicine")
            return Response({'Success': 'Successfull', 'data': serializer.data})
        else:
            return Response({'Error': serializer.errors})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    





@api_view(['POST','PATCH'])
@permission_classes((IsAuthenticated,))
def medicine_update(request):
    user = request.user
    if user:
        date = request.data.get('date', None)
        medicine = request.data.get('medicine', None)
        taken = request.data.get('taken', None)
        if user:
            customer = request.user
        else:
            customer = request.data.get('customer', None)
            if customer is None:
                return Response({"Error" : "Provide 'customer':id in data"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return Response({"Error" : "customer not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            med = Medicines.objects.get(id=medicine)
        except Medicines.DoesNotExist:
            return Response({"Error" : "Medicine not found"}, status=status.HTTP_404_NOT_FOUND)

        if date and taken is not None:
            instance, created = TakenMedicine.objects.get_or_create(medicine=med, date=date, customer=customer,
            defaults={'taken': taken})
            if not created: #then its False, so delete the entry
                instance.taken = taken
                instance.save()
            update_date(instance, "medicine")
            return Response({'succes':'Medicine Updated successfuly'}, status=status.HTTP_202_ACCEPTED)

        else:
            return Response({"Error" : "Date/taken data not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def all_medicines(request):
    user = request.user
    if not user.role == 'SALES':
        cid = user.id if user.role == 'CLIENT' else request.query_params.get('customer', None)
        # cid = 5
        if cid is not None:
            # ? new response
            data = TakenMedicine.objects.filter(customer=cid, taken=True).prefetch_related('medicine', 'medicine__time').order_by('-date')
            serializer = TakenMedicineSerializer(data, many=True)
            
            return Response(serializer.data)
        else:
            return Response({"Error" : "Customer is not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_breastfeeding_records(request):
#     user = request.user
#     date_param = request.query_params.get('date', None)

#     # Validate the date format (optional)
#     try:
#         if date_param:
#             dt.strptime(date_param, '%Y-%m-%d')
#     except ValueError:
#         return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

#     # Filter records based on date parameter
#     records = BreastfeedingRecord.objects.filter(user=user, date=date_param)
#     serializer = BreastfeedingRecordSerializer(records, many=True)
#     return Response(serializer.data)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_breastfeeding_records(request):
#     user = request.user

#     date = request.data.get('date')

#     # Check if records for the given user and date already exist
#     existing_records = BreastfeedingRecord.objects.filter(
#         user=user,
#         date=date
#     )

#     # If records already exist, do nothing
#     if existing_records:
#         return Response({'message': 'Breastfeeding records already exist for this date'}, status=status.HTTP_200_OK)
#     else:
#         # If records don't exist, create 20 new records for the user and date
#         for feeding_number in range(1, 21):
#             record = BreastfeedingRecord.objects.create(
#                 user=user,
#                 date=date,
#                 feeding_number=feeding_number,
#                 is_breastfed=False  # Set is_breastfed to False by default
#             )

#     return Response({'message': 'Breastfeeding records created successfully'}, status=status.HTTP_201_CREATED)


# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
# def edit_breastfeeding_record(request):
#     user = request.user
#     date = request.data.get('date')
#     feeding_number = request.data.get('feeding_number')

#     # Get the record for the specified user, date, and feeding_number
#     try:
#         record = BreastfeedingRecord.objects.get(
#             user=user,
#             date=date,
#             feeding_number=feeding_number
#         )
#     except BreastfeedingRecord.DoesNotExist:
#         return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

#     # Update the is_breastfed field based on the request data
#     is_breastfed = request.data.get('is_breastfed', False)
#     record.is_breastfed = is_breastfed
#     record.save()

#     serializer = BreastfeedingRecordSerializer(record)
#     return Response({'message': 'Record updated successfully', 'data': serializer.data})



# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_breastfeeding_records(request):
#     user = request.user
#     context = {}

#     # Get the date from query parameters, or use the current date if not provided
#     date = request.query_params.get('date', None)
#     if not date:
#         date = datetime.datetime.now().date()

#     # Assuming 'customer' is the related name in the User model for the BreastfeedingRecord
#     if user.role == 'CLIENT':
#         cid = user.id
#     else:
#         cid = request.query_params.get('customer', None)
#         try:
#             user = User.objects.get(id=cid)
#             cid = user.id
#         except User.DoesNotExist:
#             return Response({"error": "client not found"}, status=status.HTTP_404_NOT_FOUND)

#     # Your logic for retrieving and serializing breastfeeding records goes here
#     records = UserBreastfeedingRecord.objects.filter(user=user, date=date)
#     serializer = UserBreastfeedingRecordSerializer(records, many=True)

#     # Flatten the structure
#     flat_records = []
#     for record in serializer.data:
#         flat_record = {
#             'user': record['user'],
#             'feeding_number': record['breastfeeding_record']['feeding_number'],
#             'is_breastfed': record['breastfeeding_record']['is_breastfed'],
#             'date': record['date']
#         }
#         flat_records.append(flat_record)

#     context['breastfeeding_records'] = flat_records

#     return Response(context, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_brestfeeding_record(request):
    record=request.data.get('record_number')
    if record is not None:
        breastfeeding_record=BreastfeedingRecord.objects.create(feeding_number=record)
        return Response('done')
    else:
        return Response('number not provided ')


from django.db import transaction
from datetime import datetime, date
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_breastfeeding_records(request):
    user = request.user
    context = {}

    # Get the date from query parameters, or use the current date if not provided
    date = request.query_params.get('date', None)
    if not date:
        date = datetime.datetime.now().date()

    # Assuming 'customer' is the related name in the User model for the BreastfeedingRecord
    if user.role == 3:
        cid = user.id
    else:
        cid = request.query_params.get('customer', None)
        try:
            user = User.objects.get(id=cid)
            cid = user.id
        except User.DoesNotExist:
            return Response({"error": "client not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if records exist in UserBreastfeedingRecord
    records = UserBreastfeedingRecord.objects.filter(user=user, date=date)
    
    if not records.exists():
        # If no records, query from BreastfeedingRecord and create in UserBreastfeedingRecord
        breastfeeding_records = BreastfeedingRecord.objects.all()
        
        for record in breastfeeding_records:
            UserBreastfeedingRecord.objects.create(
                user=user,
                date=date,
                feeding_number=record.feeding_number,
                breastfeeding_record=record,
                is_breastfed=False  # Set your default value here
            )

        
        records = UserBreastfeedingRecord.objects.filter(user=user, date=date)

    serializer = UserBreastfeedingRecordSerializer(records, many=True)

    context['breastfeeding_records'] = serializer.data

    return Response(context, status=status.HTTP_200_OK)




@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def submit_breastfeeding_record(request):
    user = request.user

    if request.method == 'POST':
        date = request.data.get('date')
        feeding_number = request.data.get('feeding_number')

        # Check if records already exist for the given user, date, and feeding_number
        existing_records = UserBreastfeedingRecord.objects.filter(user=user, date=date, feeding_number=feeding_number)

        if existing_records.exists():
            return Response({'error': 'Records already exist for this date and feeding number'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create the associated BreastfeedingRecord
        is_breastfed = request.data.get('is_breastfed', False)
        breastfeeding_record, created = BreastfeedingRecord.objects.get_or_create(
            feeding_number=feeding_number,
            defaults={'is_breastfed': is_breastfed}
        )

        # Create the UserBreastfeedingRecord
        record = UserBreastfeedingRecord.objects.create(
            user=user,
            date=date,
            feeding_number=feeding_number,
            breastfeeding_record=breastfeeding_record,
            is_breastfed=is_breastfed
        )

        serializer = UserBreastfeedingRecordSerializer(record)
        return Response({'message': 'Breastfeeding record created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)

    elif request.method == 'PATCH':
        date = request.data.get('date')
        feeding_number = request.data.get('feeding_number')

        try:
            record = UserBreastfeedingRecord.objects.get(
                user=user,
                date=date,
                feeding_number=feeding_number
            )
        except UserBreastfeedingRecord.DoesNotExist:
            return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get the boolean value of is_breastfed from the request data
        is_breastfed = request.data.get('is_breastfed', None)

        if is_breastfed is not None:
            # Convert the string value to a boolean
            

            # Update the record's is_breastfed field
            record.is_breastfed = is_breastfed

            # Save the UserBreastfeedingRecord
            record.save()

            # Fetch the record again to ensure the changes are reflected
            record = UserBreastfeedingRecord.objects.get(id=record.id)

            serializer = UserBreastfeedingRecordSerializer(record)
            return Response({'message': 'Record updated successfully', 'data': serializer.data})

    else:
        return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)
    

# view for exercise tracker 
@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def add_calories_burnt(request):
    user = request.user

    if user.role != User.CLIENT:
        return Response({'error': 'Unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

    date = request.data.get('date')
    value = request.data.get('value')

    if date is None or value is None:
        return Response({'error': 'Date or value not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        instance = CaloriesBurnt.objects.get(customer=user, date=date)
        instance.value = value
        instance.save()
        return Response({'success': 'Calories updated'})
    except CaloriesBurnt.DoesNotExist:
        instance = CaloriesBurnt.objects.create(customer=user, date=date, value=value)
        return Response({'success': 'Calories added'})
    
@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def get_exercises(request):
    user=request.user
    date = request.query_params.get('date')
    if user.role==User.CLIENT:
        list=Exercise.objects.filter(user=user.id,date=date)
        serializers=ExerciseSerializer(list,many=True)
        calorie = CaloriesBurnt.objects.get(date=date,customer=user)
        calserializer=Calserializer(calorie)
        print(calserializer.data)
        context={
            'exercises':serializers.data,
            'calories':calserializer.data
        }
        return Response(context)
@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def post_exercise(request):
    user = request.user

    if user.role == User.CLIENT:
        exercise_data = request.data
        exercise_data['user'] = user

        # Add the date to the exercise_data before saving
        exercise_data['date'] = date.today()  # Assign the current date

        # Create Exercise instance directly without using serializer
        try:
            exercise = Exercise.objects.create(**exercise_data)
            return Response({'success': 'Exercise added'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['PATCH'])
def patch_exercise(request):
    id=request.data.get('id')
    date=request.data.get('date')
    done = request.data.get('done')
    print(done)
    try:
        exercise = Exercise.objects.get(id=id,date=date)
    except Exercise.DoesNotExist:
        return Response({"error": "Exercise not found"}, status=404)

    if request.method == 'PATCH':

        if done is not None:
            exercise.done = done
            exercise.save()
            return Response('done')

    return Response({"error": "Invalid request"}, status=400)


# diet tracker GET method
@api_view(['GET',])
def diet_tracker_get(request):
    user = request.user
    if user:
        if user:
            cid = user.id
        else:
            cid = request.query_params.get('customer', None)

        if cid is None:
            return Response({"Error" : "Provide 'customer': id in the params"}, status=status.HTTP_400_BAD_REQUEST)

        date = request.query_params.get('date', None)
        if date == None:
                date = datetime.datetime.now()
        if cid is not None:
            try:
                customer = User.objects.get(id=cid)
            except User.DoesNotExist:
                return Response({'user':'Customer does not exists'}, status=status.HTTP_404_NOT_FOUND)

            
            diet = DietTracker.objects.filter(customer=customer, date=date) #2011-02-10 = 2 meals
            serializer = DietTrackerSerializer(diet ,many=True)
            return Response({"Diet" : serializer.data})
        else:
            return Response({"Error" : "Customer not provided"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

# submit diet taken

@api_view(['POST','PATCH'])
@permission_classes((IsAuthenticated,))
def diet_tracker_post(request):
    user = request.user
    
    if user:
        meal_type = request.data.get('mealType', None)
        if user:
            customer = user
        else:
            cid = request.data.get('customer', None)
            if cid is not None:
                try:
                    customer = User.objects.get(id=cid,role=User.CLIENT)
                except User.DoesNotExist:
                    return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
            # return Response({'error' : "provided customer:id in params"}, status=status.HTTP_401_UNAUTHORIZED)

        if meal_type is not None:
            try:
                meal = Meal.objects.get(name=meal_type)
            except Meal.DoesNotExist:
                return Response({"error" : "Meal Type not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error" : "meal type cannot be empty"})

        data = request.data.copy()
        data['meal'] = meal.id
        data['customer'] = customer.id
        if request.data.get('date', None) is None:
            data['date'] = datetime.datetime.now().date()
        # if request.method == 'POST':
        #     serializer = DietTrackerSerializer(data=data)
        # else:
        instance, created = DietTracker.objects.get_or_create(customer=customer,meal=meal,date=data['date'])
        serializer = DietTrackerSerializer(instance, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            return Response({'success': 'Successfull', 'data' : serializer.data})
        else:
            return Response({'error' : serializer.errors})
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def add_meal(request):
    meal=request.data.get('meal')
    
    if meal:
        save=Meal.objects.create(name=meal)
        return Response('done')
    else:
        return Response('not done')

# vaccine

@api_view(['POST'])
@permission_classes((AllowAny,))
def add_vaccine(request):
    name=request.data.get('name')
    age=request.data.get('age')
    against=request.data.get('against')
    if name != None and age!=None and against !=None:
        data=Vaccinations.objects.create(name=name,age=int(age),against=against)
        return Response('vaccine added')
    else:
        return Response('vaccine not added')
    
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Vaccinations, Vaccination_user
from django.contrib.auth.models import User
from collections import defaultdict

def convert_age_to_months(age):
    if age <=0:
        return 0
    elif age <= 12:
        return 12
    elif age <= 15:
        return 15
    elif age <=18:
        return 18
    elif age <=24:
        return 24
    elif age <= 72:
        return 60  # Assuming the age range is between 4 and 6 years (48 to 72 months)
    else:
        return 0

@api_view(['GET'])
def get_vaccine(request):
    user = request.user
    vaccinations = Vaccinations.objects.all()
    response_data = defaultdict(list)  # Use defaultdict to store vaccines by months

    for vaccination in vaccinations:
        data = {
            'id':vaccination.id,
            'name': vaccination.name,
            'age': vaccination.age,
            'agent': vaccination.against,
            'status': False,
            'date': None
        }

        try:
            vaccination_user = Vaccination_user.objects.get(user=user, vaccine=vaccination)
            data['status'] = vaccination_user.status
            data['date'] = vaccination_user.date if vaccination_user.status else None
        except Vaccination_user.DoesNotExist:
            pass

        months = convert_age_to_months(vaccination.age)
        response_data[months].append(data)

    # Sort response_data based on months
    response_data = dict(sorted(response_data.items()))

    return Response(response_data)


@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def post_vaccine(request):
    User = get_user_model()
    user = request.user
    user_instance = User.objects.get(id=user.id)
    vaccination_id = request.data.get('vaccination_id')
    vac = Vaccinations.objects.get(id=vaccination_id)

    data = {
        'user': user_instance,
        'vaccine': vac,
        'status': request.data.get('status'),
        'date': request.data.get('date')
    }

    try:
        vaccination_record, created = Vaccination_user.objects.get_or_create(
            user=user_instance, vaccine=vac, defaults=data
        )

        if not created:
            # Update existing instance if it's not created
            vaccination_record.status = data['status']
            vaccination_record.date = data['date'] if data['date'] else timezone.now().date()
            vaccination_record.save()

        serializer = Vaccineserializer(vaccination_record)
        return Response(serializer.data)
    except Exception as e:
        # Handle exception appropriately
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
def post_brain_stimulation(request):
    sense=request.data.get('sense')
    month=request.data.get('month')
    ques=request.data.get('question')
    if sense or month or ques != None:
        data=Brain_sense.objects.create(sense=sense,month=month,question=ques)
        return Response('data is saved')
    else:
        return Response('enter sense,month,question')
    
#get view for baby brain
    
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_brain_stimulation(request):
    month=request.query_params.get('month')
    if month:
        user=request.user
        datas=Brain_sense.objects.filter(month=month)
        response_data=defaultdict(list)

        for data in datas:
            config={
                'id':data.id,
                'sense':data.sense,
                'month':data.month,
                'question':data.question,
                'ans':False,


            }
            try:
                data_user=Brain_sense_user.objects.get(user=user,sense=data)
                config['ans']=data_user.ans
            except:
                pass
            response_data['data'].append(config)
        response_data=dict(response_data)
        
    
        return Response(response_data)
    else:
        return Response('give month')
    
@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def patch_baby_brain(request):
    ans=request.data.get('ans')
    sense_id=request.data.get('id')
    print(ans)
    sense=Brain_sense.objects.get(id=sense_id)
    user=request.user
    data={
        'user':user,
        'sense':sense,
        'ans':ans,
        
    }
    try:
        record,created=Brain_sense_user.objects.get_or_create(user=user,sense=sense,defaults=data)

        if not created:
            
            record.ans=data['ans']
            record.save()

        return Response('done')
    except:
        return Response ('not done error occured')

#api for posting diaper
    
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def post_diaper(request):
    user = request.user
    starttime = request.data.get('st')
    startdate = request.data.get('sd')
    endtime = request.data.get('et')
    enddate = request.data.get('ed')
    wet = request.data.get('wet')
    print(user)
    print(request.data)
    if user is None or startdate is None or starttime is None or enddate is None or endtime is None or wet is None:
        print('hai')
        return Response('Enter all values correctly [st, sd, et, ed, wet]')
    else:
        try:
            record = Diapering.objects.create(
                user=user,
                start_date=startdate,
                start_time=starttime,
                end_date=enddate,
                end_time=endtime,
                wet=wet
            )
            print('created')
            return Response('Data is created')
        except Exception as e:
            print(str(e))
            return Response(str(e))
        
        #post api for sleep pattern
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def post_Sleep_pattern(request):
    user = request.user
    starttime = request.data.get('st')
    startdate = request.data.get('sd')
    endtime = request.data.get('et')
    enddate = request.data.get('ed')
    left = request.data.get('left')
    print(user)
    print(request.data)
    if user is None or startdate is None or starttime is None or enddate is None or endtime is None or left is None:
        print('hai')
        return Response('Enter all values correctly [st, sd, et, ed, left   ]')
    else:
        try:
            record = Sleep_pattern.objects.create(
                user=user,
                start_date=startdate,
                start_time=starttime,
                end_date=enddate,
                end_time=endtime,
                left=left,
            )
            print('created')
            return Response('Data is created')
        except Exception as e:
            print(str(e))
            return Response(str(e))
