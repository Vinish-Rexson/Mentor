from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import datetime
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ObjectDoesNotExist

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
    student = models.ForeignKey('MentorshipData', on_delete=models.CASCADE)
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

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    def save(self, *args, **kwargs):
        # Call the original save method to save the StudentForm instance
        super().save(*args, **kwargs)
        # After saving, sync the profile picture to the corresponding Student1 instance
        self.sync_profile_pictures()

    # Sync profile pictures from StudentForm to Student1
    def sync_profile_pictures(self):
        try:
            # Find the corresponding Student1 instance
            student1 = Student1.objects.get(mentorship_data=self.student)
            # Only update the Student1 profile picture if the current StudentForm profile picture exists
            if self.profile_picture:  # Check if StudentForm has a profile picture
                student1.profile_picture = self.profile_picture
                student1.save()  # Save the updated profile picture in Student1
            # If no profile picture in StudentForm, do nothing to Student1
            return True
        except ObjectDoesNotExist:
            # Handle case where Student1 does not exist
            return False
    def __str__(self):
        return str(self.rollno)

    



class StudentFollowupForm(models.Model):
    student = models.ForeignKey('MentorshipData', on_delete=models.CASCADE)
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




from django.db import models
from django.utils import timezone
import datetime

class MentorshipData(models.Model):
    name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=50)
    division = models.CharField(max_length=10)
    faculty_mentor = models.CharField(max_length=255, null=True, blank=True)
    be_student_mentor = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=10, blank=True)  # Year will be set based on sem
    sem = models.IntegerField(null=True)  # Semester field
    token = models.CharField(max_length=100, null=True, blank=True)
    token_created_at = models.DateTimeField(null=True, blank=True)

    def is_token_expired(self):
        if not self.token_created_at:
            return True
        return timezone.now() > self.token_created_at + datetime.timedelta(minutes=20)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Prevent set_year_based_on_sem() from being called when manually changing sem in views
        if not kwargs.pop('skip_year_update', False):
            self.set_year_based_on_sem()  # Only auto-update year if not skipped

        super().save(*args, **kwargs)
        # Ensure a corresponding Student1 instance exists
        self.ensure_student1_exists()

    def set_year_based_on_sem(self):
        """ Automatically update the year based on the current semester. """
        if self.sem in [1, 2]:
            self.year = 'FE'  # First Year
        elif self.sem in [3, 4]:
            self.year = 'SE'  # Second Year
        elif self.sem in [5, 6]:
            self.year = 'TE'  # Third Year
        elif self.sem in [7, 8]:
            self.year = 'BE'  # Final Year

    def increment_semester(self):
        if self.sem < 8:
            self.sem += 1
            if self.sem in [3, 5, 7]:
                # Update year when moving to a new academic year
                self.set_year_based_on_sem()
        self.save()

    def decrement_semester(self):
        if self.sem > 1:
            self.sem -= 1
            if self.sem in [2, 4, 6]:
                # Update year when moving to a previous academic year
                self.set_year_based_on_sem()
        self.save()

    def ensure_student1_exists(self):
        from .models import Student1  # Import here to avoid circular import
        # Check if a Student1 instance already exists
        if not Student1.objects.filter(mentorship_data=self).exists():
            # Create a new Student1 instance if it doesn't exist
            Student1.objects.create(mentorship_data=self)

            



from django.db import models
from django.contrib.auth import get_user_model
from .managers import DynamicFieldsManager  # Import the DynamicFieldsManager
from mentor_admin.models import *

User = get_user_model()

class Session(models.Model):
    student = models.ForeignKey('MentorshipData', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Dynamic fields for flexibility
    additional_info = models.JSONField(default=dict)
    
    # Many-to-many relationship for mentor_admins who can view this session
    mentor_admins = models.ManyToManyField(MentorAdmin, related_name="shared_sessions", blank=True)
    
    objects = DynamicFieldsManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.additional_info.items():
            setattr(self, key, value)

    def save(self, *args, **kwargs):
        for attr in self.additional_info.keys():
            if hasattr(self, attr):
                self.additional_info[attr] = getattr(self, attr)
        super().save(*args, **kwargs)

    def share_with_mentor_admin(self, mentor_admin):
        """Function to share a session with a mentor admin."""
        self.mentor_admins.add(mentor_admin)

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
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    def __str__(self):
        return f'{self.mentorship_data.name} ({self.mentorship_data.roll_number})'
