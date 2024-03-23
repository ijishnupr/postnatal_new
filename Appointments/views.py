
from multiprocessing import context
from Accounts.models import CustomerDetails, DoctorDetails
# from django.shortcuts import render

# from Doctor.models import AppointmentSummary
from .serializers import *
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
# from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework_api_key.permissions import HasAPIKey
from django.db.models import Q
from .models import Appointments
from django.conf import settings
from datetime import date, datetime, timedelta
# from django.utils import timezone
from twilio.rest import Client
import jwt
import requests
import json
from time import time 
from django.utils.timezone import make_aware
from django.db.models import Q,Case,When, Value, BooleanField

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def full_apointments(request):
    user = request.user
    if user.role == User.DOCTOR:
        doctor = user.id
        try:
            doctor = DoctorDetails.objects.get(user=doctor)
        except DoctorDetails.DoesNotExist:
            return JsonResponse({"error" : "doctor not found"}, status=status.HTTP_404_NOT_FOUND)
        
        current_timestamp = make_aware(datetime.now())
        dateTimeCompleted = datetime.now() - timedelta(minutes=60)

        approved = Appointments.objects.filter(doctor=doctor.id ,is_paid = True,approved=True,schedule__gte=current_timestamp - timedelta(minutes=15)).prefetch_related('customer','customer__user').order_by('-schedule').annotate(
            meeting_open=Case(
                    When(schedule__range=[current_timestamp - timedelta(minutes=15), current_timestamp], then=Value(True)),default=Value(False), output_field=BooleanField()
                )
        )
        
        rejected = Appointments.objects.filter(doctor=doctor.id , is_paid = True,rejected=True).prefetch_related('customer','customer__user').order_by('-schedule')
        completed = Appointments.objects.filter(doctor=doctor.id, is_paid = True,approved=True,schedule__lte=make_aware(dateTimeCompleted)).prefetch_related('customer','customer__user').order_by('-schedule')

        ApprovedSerializer = BookingSerializer(approved, many=True, context={'request': request})
        RejectedSerializer = BookingSerializer(rejected, many=True, context={'request': request})
        CompletedSerializer = BookingSerializer(completed, many=True, context={'request': request})

        return JsonResponse({
            # "Reschuduled" : RescheduleSerializer.data,
            "Approved" : ApprovedSerializer.data,
            "Rejected" : RejectedSerializer.data,
            "Completed" : CompletedSerializer.data
        })
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def completed(request):
    user = request.user
    if user:
        dateTimeCompleted = datetime.now() - timedelta(minutes=60)
        try:
            client = user.customer_details.get(user=user.id)
        except:
            return JsonResponse({"error" : "client not found"}, status=status.HTTP_404_NOT_FOUND)
        # dateTime = datetime.now() - timedelta(minutes=30)
        
        completedAppointments = Appointments.objects.filter(is_paid = True ,customer=client.id,approved=True, schedule__lte=make_aware(dateTimeCompleted)).prefetch_related('doctor', 'doctor__user').order_by('-schedule')
        serializer = CompletedSerializer(completedAppointments, many=True, context={'request' : request})
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def upcoming(request):
    user = request.user
    if user:
        try:
            client = user.customer_details.first()
        except:
            return JsonResponse({"error" : "client not found"}, status=status.HTTP_404_NOT_FOUND)
        timestamp = datetime.now() - timedelta(minutes=15)
        upcoming_appointments = Appointments.objects.filter(is_paid = True ,customer=client.id, approved=True, schedule__gte=make_aware(timestamp)).prefetch_related('doctor', 'doctor__user')
        serializer = UpcomingAppointmentSerializer(upcoming_appointments, many=True, context={'request':request})
    else:
        return Response({'error' : "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)
    return JsonResponse(serializer.data, safe=False)
