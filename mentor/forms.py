# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class MentorSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Mentor.objects.create(user=user)  # Create a Mentor instance
        return user
    




class StudentSemForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        
        widget=forms.TextInput(attrs={'placeholder': 'Enter student name'})
    )
    rollno = forms.CharField(
        max_length=100,
         
        widget=forms.TextInput(attrs={'placeholder': 'Enter student Roll.No'})
    )
    attendance = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter attendance percentage %', 'min': 0, 'max': 100, 'step': 0.01})
    )
    sem3cgpa = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter CGPA', 'min': 0, 'max': 10, 'step': 0.01})
    )
    question1 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter details for council/team'})
    )
    question2 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter details for co-curricular events'})
    )

    class Meta:
        model = StudentForm
        fields = ['name', 'rollno', 'attendance', 'sem3cgpa', 'question1', 'question2']


