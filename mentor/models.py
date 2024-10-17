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
    mentor_name = models.CharField(max_length=255)
    atte_ise1 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    atte_mse = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    attendance = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    cts = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    ise1 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    mse = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    semcgpa = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    counseling_dates = models.TextField(null=True, blank=True)
    

    question1 = models.TextField(null=True, blank=True)  # Allow NULL values
    question2 = models.TextField(null=True, blank=True)  # Allow NULL values
    question3 = models.TextField(null=True, blank=True)  # Allow NULL values
    question4 = models.TextField(null=True, blank=True)  # Allow NULL values
    question5 = models.TextField(null=True, blank=True)  # Allow NULL values
    question6 = models.TextField(null=True, blank=True)  # Allow NULL values
    question7 = models.TextField(null=True, blank=True)  # Allow NULL values
    question8 = models.TextField(null=True, blank=True)  # Allow NULL values
    question9 = models.TextField(null=True, blank=True)  # Allow NULL values
    question10 = models.TextField(null=True, blank=True)  # Allow NULL values
    question11 = models.TextField(null=True, blank=True)  # Allow NULL values
    question12 = models.TextField(null=True, blank=True)  # Allow NULL values
    Strengths = models.TextField(null=True, blank=True)  
    Weakness = models.TextField(null=True, blank=True) 
    Opportunities = models.TextField(null=True, blank=True)  
    Challenges = models.TextField(null=True, blank=True)  
    nao = models.TextField(null=True, blank=True)  
    ao = models.TextField(null=True, blank=True)  

    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.rollno)
    



class StudentFollowupForm(models.Model):
    name = models.CharField(max_length=255)
    rollno = models.CharField(max_length=100, unique=True) 
    mentor_name = models.CharField(max_length=255)
    atte_ise1 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    atte_mse = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    attendance = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    ise1 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    mse = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    semcgpa = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    counseling_dates = models.TextField(null=True, blank=True)
    

    question1 = models.TextField(null=True, blank=True)  # Allow NULL values
    question2 = models.TextField(null=True, blank=True)  # Allow NULL values
    question3 = models.TextField(null=True, blank=True)  # Allow NULL values
    question4 = models.TextField(null=True, blank=True)  # Allow NULL values
    question5 = models.TextField(null=True, blank=True)  # Allow NULL values
    question6 = models.TextField(null=True, blank=True)  # Allow NULL values
    question7 = models.TextField(null=True, blank=True)  # Allow NULL values
    date = models.DateTimeField(default=timezone.now)
    nao = models.TextField(null=True, blank=True)  
    ao = models.TextField(null=True, blank=True) 

    def __str__(self):
        return str(self.rollno)




class MentorshipData(models.Model):
    name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=50)
    division = models.CharField(max_length=10)
    faculty_mentor = models.CharField(max_length=255, null=True, blank=True)
    be_student_mentor = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=10)
    token = models.CharField(max_length=100, null=True, blank=True)
    token_created_at = models.DateTimeField(null=True, blank=True)

    def is_token_expired(self):
        if not self.token_created_at:
            return True
        return timezone.now() > self.token_created_at + datetime.timedelta(minutes=20)

    def __str__(self):
        return self.name



from django.db import models
from django.contrib.auth import get_user_model
from .managers import DynamicFieldsManager  # Import the DynamicFieldsManager

User = get_user_model()

class Session(models.Model):
    # Static fields for session information
    title = models.CharField(max_length=200)
    description = models.TextField()
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Dynamic fields for flexibility
    additional_info = models.JSONField(default=dict)

    # Custom manager to handle dynamic field logic
    objects = DynamicFieldsManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set attributes from additional_info on initialization
        for key, value in self.additional_info.items():
            setattr(self, key, value)

    def save(self, *args, **kwargs):
        # Before saving, ensure additional_info matches dynamic attributes
        for attr in self.additional_info.keys():
            if hasattr(self, attr):
                self.additional_info[attr] = getattr(self, attr)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session: {self.title}"

    class Meta:
        indexes = [
            models.Index(fields=['mentor']),
            models.Index(fields=['created_at']),
        ]




class Student1(models.Model):
    mentorship_data = models.ForeignKey(MentorshipData, on_delete=models.CASCADE)
    atte_ise1 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    atte_mse = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    attendance = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    cts = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    ise1 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    mse = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    semcgpa = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.mentorship_data.name} ({self.mentorship_data.roll_number})'

