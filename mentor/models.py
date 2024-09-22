from django.contrib.auth.models import User
from django.db import models

class Mentor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Student(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    section = models.CharField(max_length=1)
    science_marks = models.IntegerField()
    english_marks = models.IntegerField()
    history_marks = models.IntegerField()
    maths_marks = models.IntegerField()

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