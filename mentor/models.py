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