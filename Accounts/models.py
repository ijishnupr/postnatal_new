from django.db import models

# Create your models here.
from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

from django.contrib.auth.models import  PermissionsMixin, Group , Permission



from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, firstname, lastname, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, firstname=firstname, lastname=lastname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstname, lastname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, firstname, lastname, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ADMIN = 1
    DOCTOR = 2
    CLIENT = 3
    SALES = 4
    CONSULTANT = 5

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (DOCTOR, 'Doctor'),
        (CLIENT, 'Client'),
        (SALES, 'Sales'),
        (CONSULTANT, 'Consultant'),
    )

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=CLIENT)
    email = models.EmailField(unique=True, max_length=255, blank=False)
    firstname = models.CharField(max_length=100, default="firstname")
    lastname = models.CharField(max_length=100, null=True)
    mobile = models.CharField(max_length=12, null=True, blank=True)
    fcm_token = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Added is_staff field
    dateJoined = models.DateTimeField(default=timezone.now)
    profile_img = models.ImageField(upload_to='ProfilePic/', null=True,blank=True, default= '/ProfilePic/default.jpg')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions'
    )

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return f'{self.email} | {self.firstname}'

    objects = UserManager()

    @property
    def is_doctor(self):
        return self.role == 'DOCTOR'

class DoctorDetails(models.Model):
    FEMALE = "female"
    MALE = "male"

    GENDER_CHOICES = (
        (FEMALE,'female'),
        (MALE, 'male'),
    )


    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='docDetails',null=True)
    speciality = models.CharField(max_length=200, null=True)
    qualification = models.CharField(max_length=200, null=True)
    medicalCouncil = models.CharField(max_length=20, null=True)
    councilRegNo = models.CharField(max_length=200, null=True)
    hospitals = models.CharField(max_length=300, null=True)
    interests = models.CharField(max_length=200, null=True)
    placeOfWork = models.CharField(max_length=200, null=True)
    onlineConsultation = models.CharField(max_length=100, null=True)
    experience = models.IntegerField(default=0)
    age = models.IntegerField(default=0)
    languages = models.CharField(max_length=500 ,default='')
    location = models.CharField(max_length=200, null=True,blank=True)
    referalId = models.CharField(max_length=100, null=True,unique=True)
    price =  models.IntegerField(default=0)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=100, null=True, blank=True)

    def __str__(self):
        if self.user is not None:
            return f'{self.user.email} Name: {self.user.firstname}'
        else:
            return self.user.firstname



class CustomerDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, blank=True, null=True)
    date_of_birth_parent = models.DateField(blank=True, null=True)
    babydob = models.DateField(null=True)
    profile_img = models.ImageField(upload_to='ProfilePic/', null=True, blank=True, default='/ProfilePic/default.jpg')
    babyGender = models.CharField(max_length=10, choices=(("male", "Male"), ("female", "Female")), null=True, blank=True)
    # Add any other fields you want to store for customers
    doctor_referal = models.ForeignKey(DoctorDetails, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'Customer email: {self.user.email}'
    







class SalesTeamDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='salesDetails')
    # age = models.IntegerField()
    location = models.CharField(max_length=200, null=True, blank=True)
    passwordString = models.CharField(max_length=500)

    def __str__(self):
        if self.user is not None:
            return f'{self.user.email} Name: {self.user.firstname}'
        else:
            return self.user.firstname


class ConsultantInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='consultantDetails')
    # age = models.IntegerField()
    location = models.CharField(max_length=200, null=True, blank=True)
    passwordString = models.CharField(max_length=500)

    def __str__(self):
        if self.user is not None:
            return f'{self.user.email} Name: {self.user.firstname}'
        else:
            return self.user.firstname






