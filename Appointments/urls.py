from django.urls import path
from .views import *

urlpatterns = [
  
   path('full-appointment/', full_apointments),
   path('completed-appointment/', completed),
    path('upcoming-appointments/', upcoming),
]

