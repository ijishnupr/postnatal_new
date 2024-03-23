from django.urls import path
from .views import *

urlpatterns = [
    path('sales-dashboard-details/', sales_dashboard_details),
]
