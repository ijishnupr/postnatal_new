from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(CustomerDetails)
admin.site.register(SalesTeamDetails)
admin.site.register(ConsultantInfo)
admin.site.register(DoctorDetails)
class PersonAdmin(admin.ModelAdmin):
    search_fields=('username',)
