from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(Medicines)
admin.site.register(MedicineTime)
admin.site.register(LastUpdateDate)

admin.site.register(BreastfeedingRecord)
admin.site.register(UserBreastfeedingRecord)

