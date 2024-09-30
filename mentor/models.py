from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import datetime

class Mentor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    year = models.CharField(max_length=10)  # SE, TE, etc.
    semester = models.IntegerField()  # Sem value
    roll_number = models.CharField(max_length=10)  # Roll number from CSV
    branch = models.CharField(max_length=50)  # Branch like CE, IT, etc.
    division = models.CharField(max_length=1)  # Div value (e.g., B)
    token = models.CharField(max_length=100, null=True, blank=True)
    token_created_at = models.DateTimeField(null=True, blank=True)

    def is_token_expired(self):
        if not self.token_created_at:
            return True
        return timezone.now() > self.token_created_at + datetime.timedelta(minutes=20)

    def __str__(self):
        return self.name

    

class StudentForm(models.Model):
    name = models.CharField(max_length=255)
    rollno = models.CharField(max_length=100, unique=True) 
    attendance = models.DecimalField(max_digits=5,decimal_places=2, default=0.00)
    sem3cgpa = models.DecimalField(max_digits=5,decimal_places=2, default=0.00)
    question1 = models.TextField()
    question2 = models.TextField()
    def __str__(self):
        return (str(self.rollno))