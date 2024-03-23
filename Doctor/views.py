from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from Accounts.models import DoctorDetails, CustomerDetails
from Accounts.serializers import *
from datetime import timedelta
import datetime
from django.db.models import Q, Count,Case,When, Value, BooleanField
from .serializers import *
from django.http import JsonResponse
from django.utils.timezone import make_aware
from Accounts.models import *
from Appointments.models import Appointments
from Appointments.serializers import *
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.query import Prefetch
@api_view(['GET'])
@permission_classes([])  # You might need to define your permission classes
def customers_under_doctor(request):
    # Get the currently logged-in user, assuming you're using Django's authentication
    user = request.user

    # Find the DoctorDetails record associated with the logged-in user
    try:
        doctor = DoctorDetails.objects.get(user=user)
    except DoctorDetails.DoesNotExist:
        return Response(
            {"error": "You are not associated with any doctor account."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Retrieve all customers with doctor_referal set to the selected doctor
    customers = CustomerDetails.objects.filter(doctor_referal=doctor)

    # Serialize the customer data
    serializer = CustomerDetailsSerializer(customers, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def my_patients(request):
    user = request.user
    if user.role == User.DOCTOR:
        threshold_date = datetime.now().date() - timedelta(days=294) #42 weeks
        if user is not None:
            try:
                doctorDetailsID = user.docDetails.first().id
            except User.DoesNotExist:
                return JsonResponse({"Error" : "Doctor not found"})

            Patients = CustomerDetails.objects.filter(doctor_referal_id=doctorDetailsID, user__is_active=True)
            serializer = MyPatientSerializers(Patients, many=True, context={'request' : request})
            return JsonResponse({"customers" : serializer.data})
        else:
            return JsonResponse({"Error" : "Doctor Does not exists"})
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctors(request):
    doctors = DoctorDetails.objects.filter(
        user__is_active=True,
        user__role=User.ROLES[1][0]  # Assuming 'DOCTOR' is the second role in the choices tuple
    ).prefetch_related('user')

    serializer = DoctorDetailSerializer(doctors, many=True, context={'request': request})

    return Response({
        'status': True,
        'data': serializer.data,
        'message': 'doctors fetched'
    })
# _____________________________dashboard
from django.db.models.functions import TruncMonth

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def doctor_dashboard_details(request):    
    user = request.user
    if user:
        if id is not None:
            
            try:

                details = DoctorDetails.objects.get(user_id=user.id)
                
            except User.DoesNotExist:
                return JsonResponse({"Error" : "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
            
            threshold_date = datetime.now().date() - timedelta(days=294) #42 weeks
            totalCustomers = CustomerDetails.objects.filter(doctor_referal_id=details.id, user__is_active=True)
            
            # total patient count
            totalCount = totalCustomers.count()

            # patients in the current month
            date_threshold =  make_aware(datetime.now() - timedelta(minutes=15))
            approvalTime = make_aware(datetime.now())

            currentMonth = date_threshold.month
            customers_thisMonth = totalCustomers.filter(user__dateJoined__month=currentMonth).count()

            needsApproval = Appointments.objects.filter(doctor=user.id, approved=False,rejected=False, schedule__gte=approvalTime).count()

            todaysAppointments = Appointments.objects.filter(doctor=details.id, approved=True, schedule__date=date_threshold.date())

            consultationData = todaysAppointments.filter(schedule__gte=date_threshold).prefetch_related('customer').order_by('time').prefetch_related('customer','customer__user')[:2]
            
            todaysAppointmentsCount = todaysAppointments.count() 

            consultation = TodaysAppointmentSerializer(consultationData, many=True)
            
            graphData = Appointments.objects.filter(doctor=details.id, date__year=date_threshold.year).annotate(month=TruncMonth('date')).values('month').annotate(appointments=Count('id')).annotate(cancelled=Count('id', filter=Q(rejected=True))).values('month', 'appointments','cancelled').order_by('month')

            GdSerializer = GraphDataSerializer(graphData, many=True)
            profile_pic = user.profile_img
            print(profile_pic)
            # return "https://" + str(get_current_site(request)) + "/media/" + str(obj.profile_img)
            # else:
            #     return "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg")
            context = {
                'doctorId' : user.id,
                'approvalRequests' : needsApproval,
                'todaysAppointmentsCount' : todaysAppointmentsCount,
                'profile_pic' : "https://" + str(get_current_site(request)) + "/media/" + str(profile_pic) if profile_pic is not None else "https://" + str(get_current_site(request)) + "/media/ProfilePic/" + str("default.jpg"),
                'totalClients' : totalCount,
                'clientsThisMonth' : customers_thisMonth,
                'graphData' : GdSerializer.data,
                'latestConsultation' : consultation.data
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            return Response({"Error" : "Id not provided"})
    return Response({'error' : "no permission"}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def doctor_profile(request):
    user = request.user
    if user:
        id = user.id
    else:
        id = request.query_params.get('doctor', None)
    if not user.role == User.CONSULTANT:
        if id is not None:
            try:
                profile = DoctorDetails.objects.select_related('user').get(user_id=id)
            except DoctorDetails.DoesNotExist:
                return JsonResponse({"Error" : "Invalid id"}, status=status.HTTP_404_NOT_FOUND)
            serializer = DoctorProfileSerialzer(profile, context={'request': request})
            return JsonResponse(serializer.data)
        else:
            return JsonResponse({"Error" : "id not provided,if not doctor send via query_params"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def doctor_filter(request):
    user = request.user
    if user.role == User.CLIENT or user.role == User.DOCTOR:
        speciality = request.query_params.get('speciality', None)
        id = request.query_params.get('id', None)
        if speciality is not None:
            doctors = DoctorDetails.objects.filter(user__is_active=True, user__role=User.DOCTOR, speciality__icontains=speciality).prefetch_related('user')
            serializer = DoctorDetailSerializer(doctors, many=True, context={'request' : request})
        elif id is not None:
            doctors = DoctorDetails.objects.filter(user__is_active=True, user__role=User.DOCTOR, user__id=id).prefetch_related('user')
            serializer = DoctorDetailSerializer(doctors, many=True, context={'request' : request})
        else:
            return Response({'error' : "provide filter property"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)
    else:
        return Response({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    