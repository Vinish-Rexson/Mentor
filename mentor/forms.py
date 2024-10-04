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
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Enter student name'})
    )
    rollno = forms.CharField(
        max_length=100,
        error_messages={
            'unique': 'This Roll number has already filled the current sem form'  # Customize this as needed
        },
        widget=forms.TextInput(attrs={'placeholder': 'Enter student Roll.No'})
    )
    semcgpa = forms.DecimalField(  # Changed to match the model
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter CGPA', 'min': 0, 'max': 10, 'step': 0.01})
    )
    atte_ise1 = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter attendance for ISE1', 'min': 0, 'max': 100, 'step': 0.01})
    )
    atte_mse = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter attendance for MSE', 'min': 0, 'max': 100, 'step': 0.01})
    )
    attendance = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter attendance percentage %', 'min': 0, 'max': 100, 'step': 0.01})
    )
    cts = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter CTS', 'min': 0, 'step': 0.01})
    )
    ise1 = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter ISE1 score', 'min': 0, 'max': 100, 'step': 0.01})
    )
    mse = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter MSE score', 'min': 0, 'max': 100, 'step': 0.01})
    )
    
    question1 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter details for council/team'})
    )
    question2 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter details for co-curricular events'})
    )
    question3 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 3 detail'})
    )
    question4 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 4 detail'})
    )
    question5 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 5 detail'})
    )
    question6 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 6 detail'})
    )
    question7 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 7 detail'})
    )
    question8 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 8 detail'})
    )
    question9 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 9 detail'})
    )
    question10 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 10 detail'})
    )
    question11 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 11 detail'})
    )
    question12 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 12 detail'})
    )
    date = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Counseling Dates', 'readonly': 'readonly'}),
        required=True
    )
    mentor_name = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )



    Strengths = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Strengths', 'rows': 4})
    )
    Weakness = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Weakness', 'rows': 4})
    )
    Opportunities = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Opportunities', 'rows': 4})
    )
    Challenges = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Challenges', 'rows': 4})
    )
    nao = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Non-Academic Observations', 'rows': 4})
    )
    ao = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Academic Observations', 'rows': 4})
    )



    class Meta:
        model = StudentForm  # Ensure this is the correct model name
        fields = [
            'name', 'rollno', 'atte_ise1', 'atte_mse', 'attendance', 
            'cts', 'ise1', 'mse', 'semcgpa', 'question1', 'question2', 
            'question3', 'question4', 'question5', 'question6', 
            'question7', 'question8', 'question9', 'question10', 'question11','question12','date','mentor_name',
            'Strengths', 'Weakness', 'Opportunities', 'Challenges', 'nao', 'ao',
        ]





from django import forms
from .models import StudentFollowupForm  # Replace this with the actual model

class StudentFollowup_Form(forms.ModelForm):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Enter student name'})
    )
    rollno = forms.CharField(
        max_length=100,
        error_messages={
            'unique': 'This Roll number has already filled the current sem form'
        },
        widget=forms.TextInput(attrs={'placeholder': 'Enter student Roll.No'})
    )
    semcgpa = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter CGPA', 'min': 0, 'max': 10, 'step': 0.01})
    )
    atte_ise1 = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter attendance for ISE1', 'min': 0, 'max': 100, 'step': 0.01})
    )
    atte_mse = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter attendance for MSE', 'min': 0, 'max': 100, 'step': 0.01})
    )
    attendance = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter attendance percentage %', 'min': 0, 'max': 100, 'step': 0.01})
    )
    ise1 = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter ISE1 score', 'min': 0, 'max': 100, 'step': 0.01})
    )
    mse = forms.DecimalField(
        max_digits=5, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter MSE score', 'min': 0, 'max': 100, 'step': 0.01})
    )
    question1 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter details for council/team'})
    )
    question2 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter details for co-curricular events'})
    )
    question3 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 3 detail'})
    )
    question4 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 4 detail'})
    )
    question5 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 5 detail'})
    )
    question6 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 6 detail'})
    )
    question7 = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Question 7 detail'})
    )
    date = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Counseling Dates', 'readonly': 'readonly'}),
        required=False,
    )
    mentor_name = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    nao = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Non-Academic Observations', 'rows': 4})
    )
    ao = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Academic Observations', 'rows': 4})
    )

    class Meta:
        model = StudentFollowupForm  # This should be your actual model
        fields = [
            'name', 'rollno', 'atte_ise1', 'atte_mse', 'attendance', 
            'ise1', 'mse', 'semcgpa', 'question1', 'question2', 
            'question3', 'question4', 'question5', 'question6', 
            'question7', 'date', 'mentor_name','nao','ao',
        ]
