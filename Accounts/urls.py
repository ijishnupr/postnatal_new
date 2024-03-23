from django.contrib import admin
from django.urls import path, include
from .views import *
urlpatterns = [

    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', login_view),
    path('logout/', logout_view),
    path('get-customer-details/', get_customer_details, name='get-customer-details'),
    path('update-customer-details/', update_customer_details, name='update-customer-details'),
    path('admin-update-customer-details/',admin_update_customer_details, name='admin-update-customer-details'),
    path('doctor_registration/', doctor_registration, name='doctor_registration'),
    path('sales_team_registration/', sales_team_registration, name='sales_team_registration'),
    path('consultant_registration/', consultant_registration, name='consultant_registration'),
    
    # Admin section

    path('signup_admin/',signup_admin),
    path('login_admin/',login_admin),
    path('admin_dashboard_details/',admin_dashboard),
    path('all-doctors-list/', all_doctors),
]

   

    


