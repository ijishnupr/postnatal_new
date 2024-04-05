from django.urls import path
from .views import *

urlpatterns = [
    path('view-my-patients/', my_patients),
    path('customers_under_doctor/',customers_under_doctor, name='customers_under_doctor'),
    path('get-doctors/' , get_doctors),
    path('doctor-dashboard-details/', doctor_dashboard_details),
    path('doctor-profile/', doctor_profile),
    # Doctor filtering
    path('doctor-filter/', doctor_filter),
]