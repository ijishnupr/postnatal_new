from django.shortcuts import render
from datetime import datetime, timedelta, timezone
from django.utils import timezone as djangotimezone
from django.db.models import Q, Prefetch
from django.http import JsonResponse
from rest_framework import status
from Accounts.models import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from .serializers import *

# Create your views here.
@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def sales_dashboard_details(request):
    user = request.user
    if user:
        # allPatients = User.objects.filter(patient=True).prefetch_related('customer_details', 'customer_details__referalId','customer_details__referalId__user')
        allPatients = CustomerDetails.objects.all()
        # allPatients = CustomerDetails.objects.filter(user__is_active=True).prefetch_related('referalId', 'referalId__user',)
        # total clients count
        total_patients_count = allPatients.count()
        # detials
        totalPatients = ClientDetialSerializer(allPatients, many=True)
        # time_threshold = datetime.datetime.now() - datetime.timedelta(days=1,hours=24)
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=24)


        

        # lastUpdatedPatientSerializer = CustomerLastUpdated24hoursSerilializer(lastUpdatedPatients, many=True)
    
        # total clients this month
        month = datetime.today().month
        this_month_patients = allPatients.filter(user__dateJoined__month=month)

        # details
        # this_month_patient_details = CustomerSerializer(this_month_patients, many=True)

        # this month count
        this_month_patients_count = this_month_patients.count()

    
        return JsonResponse({
            'firstname' : user.firstname,
            'lastname' : user.lastname,
            # 'lastUpdated_in_24Hours' : lastUpdatedPatientSerializer.data,   

            'total_patients_count' : total_patients_count,

            'this_month_patients_count' : this_month_patients_count,

            # details
            'totalPatients_details' : totalPatients.data
            # 'this_month_patient_details' : this_month_patient_details.data,
            # 'diet' : dietSerializer.data,
        })
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

