from django.db import models
from django.db.models.fields import DateField, DateTimeField
from django.contrib.auth import get_user_model
User = get_user_model()


from enum import unique
from faulthandler import disable
from logging import critical
from re import S
from django.db import models
from datetime import datetime
from django.db.models.fields import DateField, DateTimeField
from django.utils.timezone import make_aware
from django.utils.timezone import now

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.


class MedicineTime(models.Model):
    name = models.CharField(max_length=100, null=True, unique=True)
    

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Medicine time(manual)'


#med by client
class Medicines(models.Model):
    date = DateField(auto_now_add=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.ForeignKey(MedicineTime, on_delete=models.CASCADE, related_name="Medicines") 
    name = models.CharField(max_length=300, null=True)

    # def __str__(self):
    #     return self.name

    class Meta:
        unique_together = ['customer', 'time', 'name']



class LastUpdateDate(models.Model):
    date = datetime.now()
    timezone_aware_date = make_aware(date)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="last_update")
    # diet = models.DateTimeField(default=now)
    medicine = models.DateTimeField(default=now)
    # activity = models.DateTimeField(default=now)
    # symptom = models.DateTimeField(default=now)
    # exercise = models.DateTimeField(default=now)
    # contraction = models.DateTimeField(default=now)

    def __str__(self):
        return self.customer.email
    

class TakenMedicine(models.Model):
    medicine = models.ForeignKey(Medicines, on_delete=models.CASCADE, related_name='MedicineDetail', null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    taken = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']
        unique_together = ['medicine', 'customer', 'date']



class BreastfeedingRecord(models.Model):
    feeding_number = models.CharField(max_length=50)
    is_breastfed = models.BooleanField(default=False)

    def __str__(self):
        return f"Breastfeeding Record - Feeding Number: {self.feeding_number}"
    

class UserBreastfeedingRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    breastfeeding_record = models.ForeignKey(BreastfeedingRecord, on_delete=models.CASCADE, related_name='user_records')
    date = models.DateField()  # Move date field to UserBreastfeedingRecord
    is_breastfed = models.BooleanField(default=False)
    feeding_number = models.IntegerField()

    def __str__(self):
        return f"User Breastfeeding Record - User: {self.user.firstname}, Record: {self.breastfeeding_record}"
    

class CaloriesBurnt(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    value = models.DecimalField(default=0, decimal_places=5, max_digits=60)
    
class Exercise(models.Model):
    name=models.CharField(max_length=100)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    done=models.BooleanField(default=False)
    date=models.DateField()

# diet's table 

class Meal(models.Model):
    name = models.CharField(max_length=255, null=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Meal (Manual)"



class DietTracker(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True)
    food = models.CharField(max_length=200)
    time = models.CharField(max_length=50)
    quantity=models.PositiveIntegerField(null=True,default=0)
    calorie=models.PositiveIntegerField(null=True,default=0)

    class Meta:
        unique_together = ['customer', 'date', 'meal']
        ordering = ['-date']

    def __str__(self):
        return self.food
    
class Vaccinations(models.Model):
    name=models.CharField(max_length=30)
    age=models.IntegerField()
    against=models.CharField(max_length=40)

    def __str__(self):
        return self.food

class Vaccination_user(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    status=models.BooleanField(default=False)
    vaccine=models.ForeignKey(Vaccinations,on_delete=models.CASCADE)
    date=models.DateField(null=True,blank=True)
   


class Brain_sense(models.Model):
    sense=models.CharField(max_length=10)
    month=models.CharField(max_length=10)
    question=models.CharField(max_length=20)
   
    
    
    def __str__(self):
        return self.question
    
class Brain_sense_user(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    sense=models.ForeignKey(Brain_sense,on_delete=models.CASCADE)
    ans=models.BooleanField(default=False)

    def __str__(self):
        return self.sense

#diapering modal
    
class Diapering(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    wet=models.BooleanField(default=True) #if the wet is true then it is wet else it is solied
    start_date=models.DateField()
    start_time=models.TimeField()
    end_date=models.DateField()
    end_time=models.TimeField()

class Sleep_pattern(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    left=models.BooleanField(default=True) #if the left is true then it is left else it is right
    start_date=models.DateField()
    start_time=models.TimeField()
    end_date=models.DateField()
    end_time=models.TimeField()

    



